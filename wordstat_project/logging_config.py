import os
import logging
from logging.handlers import TimedRotatingFileHandler
from celery.signals import after_setup_logger

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')

os.makedirs(LOG_DIR, exist_ok=True)


class UserInfoFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'user_info'):
            record.user_info = 'Unknown'
        return True


@after_setup_logger.connect
def setup_celery_logger(logger, *args, **kwargs):
    logger.setLevel(logging.INFO)
    logger.handlers = []
    file_handler = TimedRotatingFileHandler(
        os.path.join(LOG_DIR, 'celery.log'),
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(user_info)s %(message)s')
    file_handler.setFormatter(formatter)
    file_handler.addFilter(UserInfoFilter())
    logger.addHandler(file_handler)


def get_logging_config():
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'user_info': {
                '()': UserInfoFilter,
            },
        },
        'formatters': {
            'verbose': {
                'format': (
                    '%(asctime)s [%(levelname)s] %(user_info)s %(message)s'
                ),
                'style': '%',
            },
        },
        'handlers': {
            'general_file': {
                'level': 'INFO',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': os.path.join(LOG_DIR, 'general.log'),
                'when': 'midnight',
                'interval': 1,
                'backupCount': 7,
                'formatter': 'verbose',
                'filters': ['user_info'],
                'encoding': 'utf-8',
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': os.path.join(LOG_DIR, 'error.log'),
                'when': 'midnight',
                'interval': 1,
                'backupCount': 7,
                'formatter': 'verbose',
                'filters': ['user_info'],
                'encoding': 'utf-8',
            },
            'celery_file': {
                'level': 'INFO',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': os.path.join(LOG_DIR, 'celery.log'),
                'when': 'midnight',
                'interval': 1,
                'backupCount': 7,
                'formatter': 'verbose',
                'filters': ['user_info'],
                'encoding': 'utf-8',
            },
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
                'filters': ['user_info'],
            },
        },
        'loggers': {
            'django': {
                'handlers': ['general_file', 'console'],
                'level': 'INFO',
                'propagate': True,
            },
            'celery': {
                'handlers': ['celery_file', 'console'],
                'level': 'INFO',
                'propagate': True,
            },
        },
    }
