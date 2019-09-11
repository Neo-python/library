"""阿里云短信方案"""
import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


class ViewException(Exception):
    """view错误基类"""

    def __init__(self, error_code: int, message='', **kwargs):
        self.error_code = error_code
        self.message = message
        self.kwargs = kwargs

    @property
    def info(self):
        """请求相关信息"""
        return {'error_code': self.error_code, 'message': self.message, **self.kwargs}


class AliSms:
    """阿里短信接口"""

    def __init__(self, access_id, access_secret):
        self.access_id = access_id
        self.access_secret = access_secret
        self.client = AcsClient(self.access_id, self.access_secret, 'default')

    def send(self, template_code: str, phone: str, param: dict):
        """发送验证码
        :param template_code:
        :param phone:
        :param param:
        :return:
        """
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('dysmsapi.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('http')  # https | http
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')

        request.add_query_param('PhoneNumbers', phone)
        request.add_query_param('SignName', "寻宝网")
        request.add_query_param('TemplateCode', template_code)
        request.add_query_param('TemplateParam', json.dumps(param))

        response = self.client.do_action_with_exception(request)
        result = json.loads(response.decode())

        if result.get('Code', None) != 'OK':
            raise ViewException(error_code=5005, message='验证码发送失败,请联系管理员!', system_message=result.get('Message', ''))
        return response
