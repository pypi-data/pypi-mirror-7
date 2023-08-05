#encoding=utf-8

from django.http import HttpResponseForbidden
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache

import hashlib
import requests

from goldencage.models import AppWallLog
from goldencage.models import Charge
from goldencage import config

import logging
log = logging.getLogger(__name__)


waps_ips = ['219.234.85.238', '219.234.85.223',
            '219.234.85.211', '219.234.85.231',
            '127.0.0.1']


def waps_callback(request):
    ip = request.META.get("REMOTE_ADDR", None)

    if ip not in waps_ips and not request.GET.get('debug', None):
        return HttpResponseNotAllowed("incorrect IP address")
    wapslog = {}
    for key in request.GET.keys():
        wapslog[key] = request.GET[key]
    if AppWallLog.log(wapslog, provider='waps'):
        return HttpResponse("OK")
    else:
        return HttpResponseForbidden('already exists')


def youmi_callback_ios(request):
    sign = request.GET.get('sign')
    if not sign:
        return HttpResponseForbidden("miss param 'sign'")

    keys = request.GET.keys()
    keys.sort()

    src = ''.join(['%s=%s' %
                   (k, request.GET.get(k).encode('utf-8').decode('utf-8'))
                   for k in keys if k != 'sign'])
    src += settings.YOUMI_CALLBACK_SECRET
    md5 = hashlib.md5()
    md5.update(src.encode('utf-8'))
    _sign = md5.hexdigest()

    if sign != _sign:
        return HttpResponseForbidden("signature error")

    youmilog = {}
    for key in keys:
        youmilog[key] = request.GET[key]
    if AppWallLog.log(youmilog, provider='youmi_ios'):
        return HttpResponse('OK')
    else:
        return HttpResponseForbidden('already exist')

    return HttpResponseForbidden("Signature verification fail")


def appwall_callback(request, provider):
    return {'waps': waps_callback,
            'youmi_ios': youmi_callback_ios,
            }[provider](request)

alipay_public_key = config.ALIPAY_PUB_KEY


##### 支付宝回调 ########

def verify_notify_id(notify_id):
    # 检查是否合法的notify_id, 检测该id是否已被成功处理过。

    url = 'https://mapi.alipay.com/gateway.do'
    params = {'service': 'notify_verify',
              'partner': settings.ALIPAY_PID,
              'notify_id': notify_id}
    rsp = requests.get(url, params=params)
    return rsp.status_code == 200 and rsp.text == 'true'


def verify_alipay_signature(sign_type, sign, params):
    if sign_type == 'RSA':
        try:
            from Crypto.Signature import PKCS1_v1_5
            from Crypto.Hash import SHA
            keys = params.keys()
            keys.sort()
            src = '&'.join('%s=%s' % (k, params[k]) for k in keys
                           if params[k] and k not in ['sign', 'sign_type'])

            verifier = PKCS1_v1_5.new(config.ALIPAY_PUB_KEY)
            h = SHA.new(src.encode('utf-8'))
            result = verifier.verify(h, sign)
            print 'signature verify ? %d' % result
        except Exception, e:
            print e
    return True


@csrf_exempt
def alipay_callback(request):
    # 支付宝支付回调，先检查签名是否正确，再检查是否来自支付宝的请求。
    # 有效的回调，将更新用户的资产。

    keys = request.REQUEST.keys()
    data = {}
    for key in keys:
        data[key] = request.REQUEST[key]
    notify_id = data['notify_id']
    sign_type = data['sign_type']
    sign = data['sign']
    order_id = data['out_trade_no']

    nid = cache.get('ali_nid_' + hashlib.sha1(notify_id).hexdigest())
    if nid:
        return HttpResponse('error')

    if verify_notify_id(notify_id) \
            and verify_alipay_signature(sign_type, sign, data) \
            and Charge.recharge(data, provider='alipay'):
        cache.set('ali_nid_' + hashlib.sha1(notify_id).hexdigest(),
                  order_id, 90000)  # notify_id 保存25小时。
        return HttpResponse('success')
    return HttpResponse('error')
