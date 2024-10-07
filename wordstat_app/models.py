from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from encrypted_model_fields.fields import (
    EncryptedCharField,
    EncryptedTextField,
)


class CustomUser(AbstractUser):
    """Модель пользователя с уникальными полями для куков Яндекса."""
    email = models.EmailField(unique=True, blank=False)
    session_id = EncryptedTextField(blank=False, unique=True)
    yandexuid = EncryptedCharField(max_length=255, unique=True, blank=False)

    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="groups",
        blank=True,
        related_name="customuser_set",
        help_text=(
            "Группы, к которым принадлежит этот пользователь. "
            "Пользователь получит все разрешения, предоставленные "
            "каждой из его групп."
        ),
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name="user permissions",
        blank=True,
        related_name="customuser_set",
        help_text="Особые разрешения для этого пользователя",
        related_query_name="user",
    )

    def clean(self):
        super().clean()
        if (
            CustomUser.objects.filter(session_id=self.session_id)
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError("Этот Session ID уже используется")
        if (
            CustomUser.objects.filter(yandexuid=self.yandexuid)
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError("Этот Yandexuid уже используется")

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class WordstatResult(models.Model):
    """Хранит результаты анализа Wordstat."""
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="wordstat_results"
    )
    query = models.CharField(max_length=255)
    peak_months = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.query}"
