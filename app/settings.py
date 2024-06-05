

TORTOISE_ORM = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.mysql',
            'credentials': {
                'host': '127.0.0.1',
                'port': '3306',
                'user': 'root',
                'password': '74591',
                'database': 'gallery_database',
                'minsize': 1,
                'maxsize': 5,
                'charset': 'utf8mb4',
                'echo': True
            }
        }
    },
    'apps': {
        'models': {
            'models': ['models.user','models.illustration','models.image','models.server' ,'models.comment','models.notice','aerich.models'],
            'default_connection': 'default'
        }

    },
    'use_tz': False,
    'timezone': 'Asia/Shanghai'
}