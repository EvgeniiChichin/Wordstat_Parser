import os
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import redirect, render
from celery.result import AsyncResult
from .forms import (
    ExcelUploadForm,
    UserRegistrationForm,
    YandexCookiesForm,
    UserProfileForm,
)
from .models import CustomUser
from .tasks import check_cookies_task, process_excel_file_task
from .utils import letter_to_number


@login_required
def upload_file_view(request):
    """Обрабатывает загрузку Excel файла и запускает фоновую задачу."""
    if request.method == "POST":
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES["excel_file"]
            sheet_name = form.cleaned_data["sheet_name"]
            start_year = int(form.cleaned_data["start_year"])
            end_year = int(form.cleaned_data["end_year"])
            start_month = int(form.cleaned_data["start_month"])
            end_month = int(form.cleaned_data["end_month"])
            data_column = form.cleaned_data["data_col"]
            result_column = form.cleaned_data["result_col"]
            start_cell = form.cleaned_data["start_cell"]

            try:
                data_column = letter_to_number(data_column)
                result_column = letter_to_number(result_column)
            except ValueError as e:
                return JsonResponse({"error": str(e)}, status=400)

            fs = FileSystemStorage()
            filename = fs.save(excel_file.name, excel_file)
            file_path = fs.path(filename)

            task = process_excel_file_task.delay(
                file_path,
                sheet_name,
                data_column,
                result_column,
                start_cell,
                start_year,
                end_year,
                start_month,
                end_month,
                user_id=request.user.id,
            )

            return JsonResponse({"task_id": task.id})
        else:
            return JsonResponse({"error": "Неверная форма"}, status=400)
    else:
        form = ExcelUploadForm()
    return render(request, "wordstat_app/upload.html", {"form": form})


@login_required
def check_task_status(request):
    """Проверяет статус фоновой задачи и возвращает результат."""
    task_id = request.GET.get("task_id")
    task = AsyncResult(task_id)
    if task.ready():
        result = task.result
        print("Task result:", result)
        if isinstance(result, (tuple, list)) and len(result) == 3:
            new_file_path, cookies_valid, error_message = result
            if error_message:
                return JsonResponse({"status": "error",
                                     "message": error_message})
            elif not cookies_valid:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": (
                            "Ваши куки Яндекса недействительны или срок"
                            "их действия истек.Пожалуйста, обновите их."
                        ),
                    }
                )
            else:
                relative_path = os.path.relpath(
                    new_file_path, settings.MEDIA_ROOT)
                file_url = f"{settings.MEDIA_URL}{
                    relative_path.replace(os.sep, '/')}"
                return JsonResponse({"status": "completed",
                                     "file_url": file_url})
        else:
            print(f"Неожиданный формат результата: {result}")
            return JsonResponse(
                {"status": "error", "message": "Неожиданный формат результата"}
            )
    else:
        return JsonResponse({"status": "pending"})


def register_user(request):
    """Регистрирует нового пользователя."""
    if request.method == "GET":
        form = UserRegistrationForm()
        return render(request, "wordstat_app/register.html", {"form": form})
    else:
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("set_yandex_cookies")
        else:
            return render(request,
                          "wordstat_app/register.html",
                          {"form": form})


@login_required
def set_yandex_cookies(request):
    """Устанавливает куки Яндекса для пользователя."""
    if request.method == "POST":
        form = YandexCookiesForm(request.POST)
        if form.is_valid():
            session_id = form.cleaned_data["session_id"]
            yandexuid = form.cleaned_data["yandexuid"]

            task = check_cookies_task.delay(
                session_id, yandexuid, request.user.id)

            request.session['cookie_check_task_id'] = task.id

            messages.info(
                request, "Проверка куков началась. Пожалуйста, подождите.")
            return redirect('check_cookies_status')
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = YandexCookiesForm()
    return render(request,
                  "wordstat_app/set_yandex_cookies.html",
                  {"form": form})


@login_required
def check_cookies_status(request):
    """Проверяет статус установки куков."""
    task_id = request.session.get('cookie_check_task_id')
    if task_id:
        task_result = AsyncResult(task_id)
        if task_result.ready():
            is_valid, message = task_result.result
            if is_valid:
                messages.success(request, "Куки успешно сохранены!")
                return redirect("home")
            else:
                messages.error(request, f"Ошибка! {message}")
            del request.session['cookie_check_task_id']
            return redirect('set_yandex_cookies')
        else:
            return render(request,
                          "wordstat_app/check_cookies_status.html",
                          {'task_id': task_id})
    else:
        messages.error(request, "Ошибка: задача проверки куков не найдена.")
        return redirect('set_yandex_cookies')


@login_required
def home_page(request):
    """Отображает главную страницу."""
    user = CustomUser.objects.get(pk=request.user.pk)
    context = {
        "user": user,
        "session_id": user.session_id,
        "yandexuid": user.yandexuid,
    }
    return render(request, "wordstat_app/home_page.html", context)


def login_view(request):
    """Обрабатывает аутентификацию пользователя."""
    if request.method == "POST":
        email = request.POST.get("email").lower()
        password = request.POST.get("password")
        try:
            user = CustomUser.objects.get(email=email)
            username = user.username
        except CustomUser.DoesNotExist:
            messages.error(request, "Неправильный email или пароль.")
            return render(request, "wordstat_app/login.html")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("set_yandex_cookies")
        else:
            messages.error(request, "Неправильный email или пароль.")
    return render(request, "wordstat_app/login.html")


def logout_user(request):
    logout(request)
    return redirect("login")


@login_required
def profile_view(request):
    """Отображает  и  обрабатывает  форму  профиля  пользователя."""
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("profile_view")
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, "wordstat_app/profile.html", {"form": form})
