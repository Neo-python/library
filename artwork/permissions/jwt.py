"""json web token"""
import time
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

serializer = Serializer(secret_key='secret_key', expires_in=3600 * 24 * 90)


def generate_token(sub: dict, expired: int = 0, iat: float = None, **kwargs) -> str:
    """生成token
    :param sub: 用户uuid
    :param iat: jwt签发时间
    :param expired:过期时间,0为使用全局token默认过期时间
    :return:token
    """
    if iat is None:
        iat = time.time()
    if expired:
        serializer.expires_in = expired  # 设定过期时间

    info = {
        'sub': sub,
        'iat': iat,
        **kwargs
    }

    result = serializer.dumps(info)  # 直接生成token
    return result.decode()  # bytes -> str 不然无法json
