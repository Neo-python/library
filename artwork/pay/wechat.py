import requests
import uuid
import hashlib
import xmltodict
from flask import request
from artwork.pay import common


class WechatPay(object):
    """微信支付api"""
    api_url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
    refund_url = 'https://api.mch.weixin.qq.com/secapi/pay/refund'
    check_refund_url = 'https://api.mch.weixin.qq.com/pay/refundquery'
    notify_url = 'https://test_app.xunbaowang.net/interface/v1/transaction/pay/wechat/app/pay_callback/'

    def __init__(self):
        """
        :param app_id:应用编号
        :param merchant_id:商户编号
        """
        self.app_id = """config.app_id"""
        self.merchant_id = """config.merchant_app_id"""
        self.cert_path = 'plugins/public/wechat_pay/wechat_pay_cert/apiclient_cert.pem'  # 证书
        self.cert_key_path = 'plugins/public/wechat_pay/wechat_pay_cert/apiclient_key.pem'  # key

    @staticmethod
    def generate_sign(params: dict):
        """生成请求签名"""
        params = sorted(params.items(), key=lambda x: x[0], reverse=False)
        message = "&".join(f"{k}={v}" for k, v in params if k not in ['sign'])
        message = f'{message}&key={"""config.api_key"""}'
        md5 = hashlib.md5()
        md5.update(message.encode())
        return md5.hexdigest().upper()

    def base_params(self):
        """基础参数"""
        model = dict(
            appid=self.app_id,
            mch_id=self.merchant_id,
            nonce_str=uuid.uuid1().hex,
            sign=None,
            body=None,
            out_trade_no=None,
            total_fee=None,
            spbill_create_ip=request.remote_addr,
            notify_url=self.notify_url,
            trade_type='APP'
        )

        return model

    def feedback_func(self, params: dict):
        """发送返回支付参数"""
        params = {'xml': params}
        data = xmltodict.unparse(params, pretty=True)
        result = requests.post(url=self.api_url, data=data.encode()).content
        return dict(xmltodict.parse(result)['xml'])

    def apply_refund(self, params: dict):
        """
        申请退款
        params字段如下:
         total_fee: 订单总金额，单位为分
         refund_fee: 退款总金额，单位为分
         out_refund_no: 商户系统内部的退款单号，商户系统内部唯一，同一退款单号多次请求只退一笔
         transaction_id: 可选，微信订单号
         out_trade_no: 商户系统内部的订单号，与 transaction_id 二选一
         nonce_str: 随机字符串
        :return: 返回的结果数据
        """

        data = {
            'appid': self.app_id,
            'mch_id': self.merchant_id,
            'nonce_str': params['nonce_str'],
            'transaction_id': params['transaction_id'],
            'out_refund_no': params['out_refund_no'],
            'total_fee': params['total_fee'],
            'refund_fee': params['refund_fee']
        }

        sign = self.generate_sign(data)

        data.update({'sign': sign})

        xml_data = common.trans_dict_to_xml(data)  # 字典转xml

        result = requests.post(url=self.refund_url, data=xml_data, cert=(self.cert_path, self.cert_key_path))

        return result
