"""公开的随处可用的通用方法"""
import random
import datetime
from flask import jsonify


def generate_order_id():
    """生成订单编号,精度到纳秒+随机数
    """
    randint = generate_verify_code()
    time = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    return time + randint


def query_order_by(query, model, form, field):
    """查询排序封装方法
    """

    field_data = getattr(form, field).data  # 获取表单参数值
    model_field = getattr(model, field)  # 获取模型字段

    # 条件判断,生成新query对象
    if field_data:
        if field_data == 1:
            query = query.order_by(model_field)
        else:
            query = query.order_by(model_field.desc())

    return query


def orm_func(func_name: str, *args, **kwargs):
    """orm序列化,funcs参数便捷生成函数"""
    if not len(args):
        args = tuple()
    if not len(kwargs):
        kwargs = dict()
    return func_name, args, kwargs


def paginate_info(paginate, items):
    """分页信息"""
    result = {
        'total': paginate.total,
        'page': paginate.page,
        'max_page': paginate.pages,
        'items': items
    }
    return result


def result_format(error_code: int = 0, data=None, **kwargs):
    if data is None:
        data = ''
    r = {
        'error_code': error_code,
        'data': data,
        **kwargs
    }
    return jsonify(r)


def generate_verify_code(length: int = 4) -> str:
    """生成数字验证码
    :param length: 验证码长度
    """

    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


class NeoDict(dict):

    def __getattr__(self, item):
        """快捷获取字典表数据"""
        return self[item]
