"""
微信和支付宝的app支付服务会用到的一些方法
"""
import urllib
import urllib.parse
import random
import string


def trans_dict_to_xml(data_dict):
    """字典转XML"""
    data_xml = []
    for k in sorted(data_dict.keys()):  # 遍历字典排序后的key
        v = data_dict.get(k)  # 取出字典中key对应的value
        if k == 'detail' and not v.startswith('<![CDATA['):  # 添加XML标记
            v = '<![CDATA[{}]]>'.format(v)
        data_xml.append('<{key}>{value}</{key}>'.format(key=k, value=v))
    return '<xml>{}</xml>'.format(''.join(data_xml)).encode('utf-8')  # 返回XML，并转成utf-8，解决中文的问题


def generate_sign_text(params: dict, sign: bool = False, sign_type: bool = False):
    """生成签名文本
    :param params: 请求参数字典表
    :param sign: 是否需要签名字段,默认不需要.
    :param sign_type: 是否需要签名类型字段,默认不需要.
    :return:
    """

    if sign is False:
        params.pop('sign', None)

    if sign_type is False:
        params.pop('sign_type', None)

    params = sorted(params.items(), key=lambda x: x[0], reverse=False)

    message = "&".join(f"{k}={v}" for k, v in params)

    message = urllib.parse.unquote(message)  # unquote('abc%20def') -> 'abc def'
    return message


def get_random_str():
    """随机生成32位字符串+数字
    random.sample(element, 32) 取32次随机元素 返回32位随机元素列表
    :return:
    """
    # 从指定序列中随机获取指定长度的片断, ascii_letters是生成所有字母，从a-z和A-Z, digits是生成所有数字0-9
    random_str = ''.join(random.sample(string.ascii_letters + string.digits, 32))
    return random_str
