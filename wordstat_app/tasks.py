from celery import shared_task
from celery.utils.log import get_task_logger
from .cookie_validator import check_cookies
from .models import CustomUser
from .script import process_excel_file

logger = get_task_logger(__name__)


@shared_task
def process_excel_file_task(
    file_path,
    sheet_name,
    data_column,
    result_column,
    start_cell,
    start_year,
    end_year,
    start_month,
    end_month,
    user_id,
):
    """
    Обрабатывает Excel файл в фоновом режиме.

    Извлекает данные из указанного Excel файла, обрабатывает их
    и сохраняет результат.
    """
    try:
        user = CustomUser.objects.get(pk=user_id)
        user_info = f"User: {user.email}"
    except CustomUser.DoesNotExist:
        user_info = f"Неизвестный пользователь (ID: {user_id})"
        logger.error(f"[{user_info}] Пользователь не найден",
                     extra={'user_info': user_info})
        return {"status": "Ошибка", "message": "Пользователь не найден"}

    logger.info(f"[{user_info}] Начало обработки Excel файла",
                extra={'user_info': user_info})
    result = process_excel_file(
        file_path,
        sheet_name,
        data_column,
        result_column,
        start_cell,
        start_year,
        end_year,
        start_month,
        end_month,
        user=user,
        user_info=user_info
    )
    logger.info(f"[{user_info}] Завершение обработки Excel файла",
                extra={'user_info': user_info})
    return result


@shared_task
def check_cookies_task(session_id, yandexuid, user_id):
    """
    Проверяет куки Яндекса в фоновом режиме.

    Проверяет валидность переданных куков и сохраняет их
    в модели пользователя, если они действительны.
    """
    try:
        user = CustomUser.objects.get(pk=user_id)
        user_info = f"User: {user.email}"
    except CustomUser.DoesNotExist:
        user_info = f"Неизвестный пользователь (ID: {user_id})"
        logger.error(f"[{user_info}] Пользователь не найден", extra={
                     'user_info': user_info})
        return False, "Ошибка: пользователь не найден"

    logger.info(f"[{user_info}] Проверка cookies",
                extra={'user_info': user_info})
    is_valid, message = check_cookies(
        session_id, yandexuid, user_info=user_info)
    if is_valid:
        user.session_id = session_id
        user.yandexuid = yandexuid
        user.save()
        logger.info(f"[{user_info}] Cookies успешно сохранены",
                    extra={'user_info': user_info})
    else:
        logger.warning(f"[{user_info}] Ошибка при проверке cookies: {
                       message}", extra={'user_info': user_info})
    return is_valid, message
