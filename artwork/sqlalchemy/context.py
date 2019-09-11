"""DB对象上下文相关"""

from functools import wraps


def db_session(func):
    @wraps(func)
    def inner(*args, **kwargs):
        # 伪代码: app = Flask()
        app = """from run_celery import app"""
        with app.app_context():
            return func(*args, **kwargs)

    return inner