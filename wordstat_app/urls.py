from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .views import (
    register_user,
    set_yandex_cookies,
    check_cookies_status,
    home_page,
    upload_file_view,
    logout_user,
    profile_view,
    check_task_status,
    login_view,
)

urlpatterns = [
    path("", login_view, name="login"),
    path("register/", register_user, name="register"),
    path("set-yandex-cookies/", set_yandex_cookies, name="set_yandex_cookies"),
    path('check_cookies_status/', check_cookies_status, name='check_cookies_status'),
    path("home/", home_page, name="home"),
    path("upload/", upload_file_view, name="upload"),
    path("check-task-status/", check_task_status, name="check_task_status"),
    path("logout/", logout_user, name="logout"),
    path("profile/", profile_view, name="profile_view"),
    path(
        "change-password/",
        auth_views.PasswordChangeView.as_view(
            template_name="wordstat_app/change_password.html",
            success_url="/profile/"
        ),
        name="change_password",
    ),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="wordstat_app/password_reset.html"
        ),
        name="password_reset",
    ),
    path(
        "password_reset_done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="wordstat_app/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password_reset_confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="wordstat_app/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password_reset_complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="wordstat_app/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
