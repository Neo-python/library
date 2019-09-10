"""ORM模型基类与基础字段
author:Neo
"""

import copy
import datetime
import decimal
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, SmallInteger, TIMESTAMP, Integer

db = SQLAlchemy()


class Common(object):
    """orm通用操作
    免去了需要大量重复声明的字段: {id, status, create_time}
    _privacy_fields: 字段的作用为在模型数据序列化时,作为fields过滤字段
    """

    id = Column(Integer, primary_key=True, autoincrement=True, comment='自动编号')
    status = Column(SmallInteger, default=1)
    create_time = Column(TIMESTAMP, default=datetime.datetime.now)

    _privacy_fields = {'status'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def _columns(self):
        """得到模型全字段名"""

        return [item.name for item in self.__class__.__table__.columns]

    def delete(self):
        """逻辑删除"""

        self.status = 0
        return self

    def delete_true(self):
        """物理删除"""

        db.session.delete(self)
        return self

    def direct_flush_(self):
        """直接预提交"""

        self.direct_add_()
        self.flush_()
        return self

    def flush_(self):
        """预提交，等于提交到数据库内存，还未写入数据库文件"""

        db.session.flush()
        return self

    def direct_add_(self):
        """直接添加事务"""

        db.session.add(self)
        return self

    def direct_commit_(self):
        """添加事务并且提交"""

        self.direct_add_()
        db.session.commit()
        return self

    def direct_update_(self):
        """直接提交事务"""

        db.session.commit()
        return self

    def direct_delete_(self):
        """直接删除"""

        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def static_commit_():
        """直接提交.目的是尽量少直接引入db对象,集成在模型内"""

        db.session.commit()

    @staticmethod
    def static_flush_():
        """直接预提交"""

        db.session.flush()

    def set_attrs(self, attrs_dict):
        """批量更新模型的字段数据
        配合WTF表单快速更新模型数据
        示例: model.set_attrs(wtf_form.data)
        :param attrs_dict: {field:value}
        :return: self
        """

        for key, value in attrs_dict.items():
            if key in self._columns:
                setattr(self, key, value)
        return self

    def to_dict_(self, fields: set = None, funcs: list = None) -> dict:
        """返回字典表数据
        :param funcs: 在序列化后需要被调用的模型方法函数名,通过可变对象dict作为参数传递进函数时,是作为引用对象的特性而实现.
        :param fields: 允许被序列化的字段
        :return: dict({'field_name': field_value})
        """

        result = dict()

        # 默认为全字段都是允许序列化的
        if fields is None:
            fields = set(self._columns)

        if funcs is None:
            funcs = list()

        for column in fields:
            value = getattr(self, column)

            # 格式化时间类型字段
            if isinstance(value, datetime.datetime):
                value = value.strftime('%Y-%m-%d %H:%M:%S')

            # 格式化Decimal类型字段
            elif isinstance(value, decimal.Decimal):
                value = float(value)

            result[column] = value  # 将字段名与字段值关联

        # 通过funcs 添加额外的数据内容
        for func in funcs:
            func, args, kwargs = func
            getattr(self, func)(result, *args, **kwargs)

        return result

    def serialization(self, increase: set = None, remove: set = None, funcs: list = None) -> dict:
        """序列化指定字段
        :param funcs: 序列化后需要调用的函数名与参数,示例:('func_name', tuple(), dict())
        :param increase: 需要(增加/显示)的序列化输出的字段
        :param remove: 需要(去除/隐藏)的序列化输出的字段
        :return: dict({'field_name': field_value})
        """

        if increase is None:
            increase = set()

        if remove is None:
            remove = set()

        if funcs is None:
            funcs = list()

        privacy_fields = copy.copy(self._privacy_fields)  # 拷贝默认隐藏字段,不影响到全局模型的序列化输出

        all_field = set(name.name for name in self.__table__._columns)  # 获得模型所有字段

        privacy_fields = privacy_fields - increase  # 去除需要被隐藏的字段
        privacy_fields = privacy_fields | remove  # 追加需要被隐藏的字段

        all_field = all_field - privacy_fields  # 从模型原型所有的可序列化字段中 去除需要被隐藏的字段

        return self.to_dict_(fields=all_field, funcs=funcs)  # 开始序列化

    @property
    def check_create_time_today(self):
        """检查记录时间是否属于当天内"""

        create_time = self.create_time.strftime("%Y-%m-%d")
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        return create_time == now

    def update_create_time(self, new_time: int = None):
        """更新数据create_time字段
        此方法的作用是,在记录重复数据时,系统只保留一条重复数据时.直接更新时间即可.
        默认更新到当前时间
        :param new_time:指定时间
        """

        self.create_time = datetime.datetime.now()
        self.direct_update_()
        return self

    def __str__(self):
        """print内置方法打印对象,优先打印__str__"""

        description = ', '.join([f'{column.name}={getattr(self, column.name)}' for column in self.__table__._columns])
        return f'<{description}>'

    def __repr__(self):
        """想要此特殊方法被模型继承,需要将Common继承顺序排在ORM基类之前"""

        return f'<class \'{self.__class__.__name__}\' id={self.id if self.id else None}>'


class PasswordModel(object):
    """有密码的模型
    模型必须有self._password字段
    """

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw: str) -> None:
        """原始密码加密
        :param raw: 用户输入的原始密码
        """
        self._password = generate_password_hash(raw)

    def check_password(self, raw: str) -> bool:
        """检验用户输入的原始密码
        :param raw: 用户输入的原始密码
        """
        return check_password_hash(self._password, raw)
