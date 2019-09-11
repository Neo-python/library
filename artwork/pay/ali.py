import logging
import uuid
import datetime
import json
import requests
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradeAppPayModel import AlipayTradeAppPayModel
from alipay.aop.api.request.AlipayTradeAppPayRequest import AlipayTradeAppPayRequest
from alipay.aop.api.util.SignatureUtils import sign_with_rsa2
from artwork.pay import common

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    filemode='a', )
logger = logging.getLogger('')


class AliPay:
    callback_url = 'https://test_app.xunbaowang.net/interface/v1/transaction/pay/ali/app/pay_callback/'
    http_api_url = 'https://openapi.alipay.com/gateway.do'

    def __init__(self):
        self.client = self._init()

    def _init(self):
        alipay_client_config = AlipayClientConfig()
        alipay_client_config.app_id = """config.app_id"""
        alipay_client_config.app_private_key = """config.alipay_private_key"""
        alipay_client_config.alipay_public_key = """config.alipay_public_key"""
        return DefaultAlipayClient(alipay_client_config=alipay_client_config, logger=logger)

    def pay_apply(self, order_id, price: float, subject: str, content: str, back_params: str = None,
                  timeout_express=None, callback_url: str = callback_url):
        """
        :param timeout_express: 超时时间,分钟
        :param order_id: 订单编号
        :param price: 总价,金额
        :param subject: 标题
        :param content:
        :param back_params:公用回传参数,必须进行 UrlEncode
        :param callback_url:
        :return:
        """
        model = AlipayTradeAppPayModel()
        model.timeout_express = f'{round(timeout_express, 4)}m'
        model.total_amount = float(price)
        model.seller_id = """config.alipay_account"""
        model.product_code = "QUICK_MSECURITY_PAY"  # 固定值
        model.body = content[:128]  # 接口最长支持128个字符
        model.subject = subject
        model.out_trade_no = order_id

        if back_params:
            model.passback_params = back_params

        request = AlipayTradeAppPayRequest(biz_model=model)
        request.notify_url = callback_url
        return self.client.sdk_execute(request)

    def trade_refund(self, biz_content: dict, charset: str = 'utf-8', sign_type='RSA2', version='1.0'):
        """退款
        :param biz_content: 必选字段:"out_trade_no","trade_no","refund_amount","refund_reason",""
        :param charset:
        :param sign_type:
        :param version:
        :return:
        """

        params = {
            'app_id': """config.app_id""", 'method': 'alipay.trade.refund', 'charset': charset, 'sign_type': sign_type,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'version': version,
            'biz_content': json.dumps(biz_content)
        }
        sign = sign_with_rsa2("""config.alipay_private_key""",
                              sign_content=common.generate_sign_text(params, sign_type=True), charset=charset)
        params.update({'sign': sign})

        return requests.get(url=self.http_api_url, params=params)

    def trade_close(self, biz_content: dict, charset: str = 'utf-8', sign_type='RSA2', version='1.0'):
        """关闭交易
        :param biz_content: 必选字段:"out_trade_no","trade_no",
        :param charset: 请求参数编码
        :param sign_type: 签名加密算法
        :return:
        """
        params = {
            'app_id': """config.app_id""", 'method': 'alipay.trade.close', 'charset': charset, 'sign_type': sign_type,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'version': version,
            'biz_content': json.dumps(biz_content)
        }
        sign = sign_with_rsa2("""config.alipay_private_key""",
                              sign_content=common.generate_sign_text(params, sign_type=True), charset=charset)
        params.update({'sign': sign})

        return requests.get(url=self.http_api_url, params=params)

    def trade_query(self, biz_content: dict, charset: str = 'utf-8', sign_type='RSA2', version='1.0'):
        """交易查询
        :param biz_content:请求参数的集合 可选字段:["out_trade_no", "trade_no", "org_pid"]
        :param charset:请求参数编码
        :param sign_type: 签名加密算法
        :return:
        """
        params = {
            'app_id': """config.app_id""", 'method': 'alipay.trade.query', 'charset': charset, 'sign_type': sign_type,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'version': version,
            'biz_content': json.dumps(biz_content)
        }
        sign = sign_with_rsa2("""config.alipay_private_key""",
                              sign_content=common.generate_sign_text(params, sign_type=True), charset=charset)
        params.update({'sign': sign})

        return requests.get(url=self.http_api_url, params=params)

    def test_func(self):
        """测试函数"""
        model = AlipayTradeAppPayModel()
        model.timeout_express = "90m"
        model.total_amount = "0.01"
        model.seller_id = """config.alipay_account"""
        model.product_code = "QUICK_MSECURITY_PAY"
        model.body = "Iphone6 16G"
        model.subject = "iphone"
        model.out_trade_no = uuid.uuid1().hex
        request = AlipayTradeAppPayRequest(biz_model=model)
        request.notify_url = 'https://test_app.xunbaowang.net/interface/v1/transaction/pay/ali/app/pay_callback/'
        return self.client.sdk_execute(request)
