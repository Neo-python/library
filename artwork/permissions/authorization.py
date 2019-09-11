"""auth"""
import json
from functools import wraps
from itsdangerous import BadSignature
from flask import g, request
from flask_httpauth import HTTPTokenAuth
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from artwork.common import error, public

auth = HTTPTokenAuth()
serializer = Serializer(secret_key="""config.SECRET_KEY""", expires_in=3600 * 24 * 90)


def authorization_to_dict(authorization: str) -> dict:
    """HTTP头Authorization转换数据类型为dict"""
    items = authorization.split(',')  # 以','拆分出键值对
    items = (i.split('=') for i in items)  # 以'='拆分键值对
    try:
        result = dict(items)  # 转换为字典表
    except BaseException as err:
        print(err)
        result = dict()  # 转换失败 设置空字典表返回
    return result


@auth.verify_token
def _verify_token(authorization):
    """验证token,@auth.login_required 所调用的验证逻辑
    :param authorization:HTTP.Headers.Authorization
    """
    authorization = authorization_to_dict(authorization)  # 解析Authorization数据,返回dict类型数据集合

    token = authorization.get('token', None)  # 获取token值
    try:
        assert token, 'authorization failed'
        payload = serializer.loads(token)  # 尝试解密token
        sub = payload.get('sub')  # 获取用户uuid
        iat = """Redis.get(f'{config.USER_REDIS_KEY_PREFIX}_IAT_{sub}')"""
        if not iat:
            raise error.ViewException(error_code=4003, message='token失效')
        if float(iat) != payload.get('iat'):
            raise error.ViewException(error_code=4003, message='token失效')
    except AssertionError as err:
        raise error.ViewException(error_code=4001, message=str(err))

    except BadSignature:
        raise error.ViewException(error_code=4002, message='signature failure')
    else:
        g.user = payload  # 刷新token时调用
        return True


class LoginVerify:
    """login权限装饰器验证逻辑"""

    def demo(self, args):
        """示例验证逻辑"""
        raise Exception()


def login(**login_kwargs):
    """登录权限验证装饰器.
    login调用示例: @login(demo={'args':0})
    login_kwargs = {func_name:{args_name:args}}
    """

    def outer(func):
        @auth.login_required
        @wraps(func)
        def inner(*args, **kwargs):
            """自定义验证逻辑"""
            verify = LoginVerify()
            for func_name, func_kwargs in login_kwargs.items():
                verify_func = getattr(verify, func_name)
                verify_func(**func_kwargs)
            return func(*args, **kwargs)

        return inner

    return outer


def check_sign_in():
    """检查登录状态"""

    authorization = request.headers.get('Authorization')
    if authorization:
        authorization = authorization.replace('Bearer ', '')

    if authorization:
        try:
            _verify_token(authorization=authorization)
        except Exception:
            return None
        else:
            return True
    else:
        return None


def get_user_info(error_out: bool = True):
    """获取用户数据:缓存数据"""

    def _get_user_info():
        _info = getattr(g, '_info', None)
        if _info:
            return _info
        user_info = getattr(g, 'user', None)
        if user_info and user_info.get('sub', None):
            user_uuid = user_info.get('sub')
            g._info = """Redis.get(f'{config.USER_REDIS_KEY_PREFIX}_info_{user_uuid}')"""
            return g._info
        else:
            return None

    result = _get_user_info()
    if result:
        try:
            result = public.NeoDict(**json.loads(result))
        except:
            raise error.ViewException(error_code=5001, message='用户数据异常!!!')
        else:
            return result
    elif error_out is True:
        raise error.ViewException(error_code=5001, message='用户数据异常!!!')
