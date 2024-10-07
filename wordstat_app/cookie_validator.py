from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


def generate_yandex_cookies(session_id, yandexuid):
    """Формирует куки Яндекса для Selenium."""
    logger.info(f"Генерация куков: session_id={session_id}, "
                f"yandexuid={yandexuid}")
    return [
        {
            "name": "Session_id",
            "value": session_id,
            "domain": ".yandex.ru",
            "hostOnly": False,
            "path": "/",
            "secure": True,
            "httpOnly": True,
            "session": False,
        },
        {
            "name": "yandexuid",
            "value": yandexuid,
            "domain": ".yandex.ru",
            "hostOnly": False,
            "path": "/",
            "secure": True,
            "httpOnly": False,
            "session": False,
        },
    ]


def check_cookies(session_id, yandexuid, user_info=None):
    """Проверяет валидность куков Яндекса."""
    driver = None
    try:
        options = Options()
        options.add_argument('-headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        service = Service('/usr/local/bin/geckodriver')
        driver = webdriver.Firefox(service=service, options=options)
        logger.info("Запуск Firefox драйвера и открытие страницы",
                    extra={'user_info': user_info})

        driver.get("https://wordstat.yandex.ru/")

        cookies = generate_yandex_cookies(session_id, yandexuid)
        logger.info(f"Добавление куков: {cookies}", extra={
                    'user_info': user_info})
        for cookie in cookies:
            driver.add_cookie(cookie)

        logger.info("Перезагрузка страницы с новыми куками",
                    extra={'user_info': user_info})
        driver.get("https://wordstat.yandex.ru/")

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "user-pic"))
            )
            logger.info("Куки успешно проверены. Элемент найден.",
                        extra={'user_info': user_info})
            return True, "Куки корректные, пользователь авторизован."
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            return False, (
                "Куки некорректные. Пожалуйста, "
                "проверьте введенные данные."
            )
    except Exception as e:
        logger.error(f"Ошибка проверки куки: {
                     e}", extra={'user_info': user_info})
        return False, "Ошибка при проверке куков. Попробуйте еще раз."
    finally:
        if driver:
            driver.quit()
            logger.info("Закрытие драйвера.", extra={'user_info': user_info})
