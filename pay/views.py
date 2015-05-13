# encoding: utf-8
'''
Created on 2015-05-05

@author: xiaowei
'''

from alipay.create_direct_pay_by_user.forms import AliPayDirectPayForm
from alipay.helpers import make_sign, get_form_data
from django.conf import settings
from django.shortcuts import render
from pay.forms import PaymentForm
from utils.helper import json_response, decrypt
import hashlib
import requests
import urllib2


def pay_by_alipay(request):
    data = {'status': 400}
    request_params = getattr(request, request.method)
    signed_request = request_params.get('signed_request', '')
    signed_request = signed_request.split('.')
    if len(signed_request) == 2:
        sign, pay_data = signed_request[0], signed_request[1]
    else:
        return json_response(data)
    pay_data = decrypt(pay_data, settings.PRIVATE_KEY)

    pay_data = pay_data.split('&')
    pay_data.sort()
    pay_data = '&'.join(pay_data)

    sign_cal = hashlib.md5('%s%s' % (pay_data, settings.PRIVATE_KEY)).hexdigest()
    print sign, sign_cal
    #if sign_cal != sign:
    #    return json_response(data)
    params = Param('?%s' % pay_data)

    total_fee = params.get('total_fee', 0.01)
    domain_buy = params.get('domain_buy', '')
    service = params.get('service', '')
    user_id = params.get('user_id', '')
    out_trade_no = params.get('out_trade_no', '')
    subject = params.get('subject', '')
    body = params.get('body', '')


    # alipay form
    alipay_dict = {
            "_input_charset": 'utf-8',
            'notify_url': '%s/alipay/nofify-async/' % settings.DOMAIN,
            'return_url': '%s/alipay/return/?out_trade_no=%s' % (settings.DOMAIN,
            	                                                 out_trade_no),
            'sign_type': 'MD5',
            # 'sign': '',
            # 'error_notify_url': '',
            'out_trade_no': out_trade_no,
            'subject': subject,
            # 'buyer_id': '',
            # 'seller_account_name': '',
            # 'buyer_account_name': '',
            'seller_email': settings.ALIPAY_SELLER_EMAIL,
            # 'price': '',
            'total_fee': 0.01,
            # 'quantity': '',
            # 超时时间m-分钟,h-小时,d-天,1c-当天(无论交易何时创建,都在0点关闭)。
            # 该参数数值不接受小数点, 如1.5h,可转换为 90m
            # 'it_b_pay': '1h',
            'body': body,
            # 'show_url': '',
            # 'discount': '',
            # 'need_ctu_check': 'Y',
            # 'royalty_type': '',
            # 'royalty_parameters': '',
            'anti_phishing_key': 'AABBCDDEG',
            # 'exter_invoke_ip': '',
            'extra_common_param': 'This is a test request',
            # 'extend_param': '',
            'default_login': 'Y',
            # 'product_type': '',
            # 'token': '',
            }
    alipay_form = AliPayDirectPayForm(auto_id=False, initial=alipay_dict)
    data = get_form_data(alipay_form)
    alipay_form['sign'].field.initial = make_sign(data)
    data = get_form_data(alipay_form)
    request_url = alipay_form.get_action()
    for key, value in data.items():
        if isinstance(value, unicode):
            v = value.encode(alipay_form.initial['_input_charset'])
        else:
            v = value.decode('utf-8').encode(alipay_form.initial['_input_charset']) if hasattr(value, 'decode') else value
        try:
            v = urllib2.quote(v)
        except AttributeError:
            pass
        request_url += "&%s=%s" % (key, v)
    print request_url
    return_data = {}
    return_data['alipay_url'] = request_url
    return_data.update({'return_code': 0})
    return json_response(return_data)


def nofify_async(request):
	pass


def return_func(request):
    out_trade_no = request.GET.get('out_trade_no', '')
    print out_trade_no
    url = 'http://10.18.103.31:8888/api/alipay/open/'
    url = '%s/api/alipay/open/' % settings.IFRAME_CLOUD_URL
    params = "out_trade_no=%s" % ( 
             out_trade_no)
    private_key = settings.PRIVATE_KEY
    sign = hashlib.md5('%s%s' % (params, private_key)).hexdigest()
    signed_request = "%s.%s" % (sign, encrypt(params, private_key))
    data = {'signed_request': signed_request}
    r = requests.post(url, data=data)
    print client_ip
    print r.text
    res = r.json()
    return render(request, 'pay.html', {'result': res.status})
