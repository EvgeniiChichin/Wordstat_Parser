from datetime import datetime
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import FileExtensionValidator, RegexValidator
from .models import CustomUser


class ExcelUploadForm(forms.Form):
    """Форма загрузки Excel файла с данными."""
    excel_file = forms.FileField(
        label="Выберите файл Excel",
        validators=[FileExtensionValidator(
            allowed_extensions=["xlsx", "xls"])],
    )
    sheet_name = forms.CharField(label="Имя листа", max_length=100)
    current_year = datetime.now().year
    YEAR_CHOICES = [(year, str(year))
                    for year in range(2023, current_year + 1)]
    MONTH_CHOICES = [
        (1, "Январь"),
        (2, "Февраль"),
        (3, "Март"),
        (4, "Апрель"),
        (5, "Май"),
        (6, "Июнь"),
        (7, "Июль"),
        (8, "Август"),
        (9, "Сентябрь"),
        (10, "Октябрь"),
        (11, "Ноябрь"),
        (12, "Декабрь"),
    ]

    start_year = forms.ChoiceField(label="Год начала:", choices=YEAR_CHOICES)
    end_year = forms.ChoiceField(label="Год окончания:", choices=YEAR_CHOICES)
    start_month = forms.ChoiceField(
        label="Месяц начала:", choices=MONTH_CHOICES)
    end_month = forms.ChoiceField(
        label="Месяц окончания:", choices=MONTH_CHOICES)
    start_cell = forms.IntegerField(
        label="Начальная строка:", min_value=1, initial=1)
    data_col = forms.CharField(
        label="Столбец с запросами (буква):", max_length=1, initial='A')
    result_col = forms.CharField(
        label="Столбец для результатов (буква):", max_length=1, initial='B')

    def clean(self):
        """Дополнительная валидация дат."""
        cleaned_data = super().clean()
        start_year = cleaned_data.get("start_year")
        end_year = cleaned_data.get("end_year")
        start_month = cleaned_data.get("start_month")
        end_month = cleaned_data.get("end_month")

        if start_year and end_year:
            if int(start_year) > int(end_year):
                self.add_error(
                    "start_year",
                    "Год начала не может быть больше года окончания"
                )
                self.add_error(
                    "end_year",
                    "Год начала не может быть больше года окончания"
                )

        if start_year == end_year and start_month and end_month:
            if int(start_month) > int(end_month):
                self.add_error(
                    "start_month",
                    (
                        "Месяц начала не может быть больше месяца окончания "
                        "для одного года"
                    ),
                )
                self.add_error(
                    "end_month",
                    (
                        "Месяц начала не может быть больше месяца окончания"
                        "для одного года",
                    )
                )

        return cleaned_data


class UserRegistrationForm(UserCreationForm):
    """Форма регистрации пользователя."""
    class Meta:
        model = CustomUser
        fields = ("username", "email", "first_name", "last_name")

    username = forms.CharField(
        label="Имя пользователя",
        max_length=50,
        help_text="Имя пользователя должно быть уникальным",
        required=True,
        validators=[
            RegexValidator(
                r"^[\w.@+-]+$",
                (
                    "Имя пользователя может содержать только буквы, "
                    "цифры и символы: . @ + -"
                ),
            )
        ],
    )

    email = forms.EmailField(
        label="Электронная почта",
        max_length=254,
        help_text="Электронная почта должна быть уникальной",
        required=True,
    )

    first_name = forms.CharField(
        label="Имя",
        max_length=50,
        help_text="Введите свое имя",
        required=True,
    )

    last_name = forms.CharField(
        label="Фамилия",
        max_length=50,
        help_text="Введите свою фамилию",
        required=True,
    )


class YandexCookiesForm(forms.Form):
    """Форма для ввода куков Яндекса."""
    session_id = forms.CharField(
        label="Session ID",
        max_length=500,
        help_text="Введите value session_id",
        required=True,
    )
    yandexuid = forms.CharField(
        label="Yandexuid",
        max_length=250,
        help_text="Введите value yandexuid",
        required=True,
    )

    def clean(self):
        """Проверяет уникальность  куков."""
        cleaned_data = super().clean()
        session_id = cleaned_data.get("session_id")
        yandexuid = cleaned_data.get("yandexuid")

        if CustomUser.objects.filter(session_id=session_id).exists():
            raise forms.ValidationError("Этот Session ID уже используется")
        if CustomUser.objects.filter(yandexuid=yandexuid).exists():
            raise forms.ValidationError("Этот Yandexuid уже используется")

        return cleaned_data


class UserProfileForm(forms.ModelForm):
    """Форма редактирования  профиля пользователя."""
    class Meta:
        model = get_user_model()
        fields = ("username", "email", "first_name", "last_name")

    username = forms.CharField(
        label="Имя пользователя",
        max_length=50,
        help_text="Имя пользователя должно быть уникальным",
        validators=[
            RegexValidator(
                r"^[\w.@+-]+$",
                (
                    "Имя пользователя может содержать только буквы,"
                    "цифры и символы: . @ + -",
                ),
            )
        ],
    )

    email = forms.EmailField(
        label="Электронная почта",
        max_length=254,
        help_text="Электронная почта должна быть уникальной",
    )

    first_name = forms.CharField(
        label="Имя",
        max_length=50,
        help_text="Введите свое имя",
    )

    last_name = forms.CharField(
        label="Фамилия",
        max_length=50,
        help_text="Введите свою фамилию",
    )

    def __init__(self, *args, **kwargs):
        """Делает все поля необязательными."""
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = False


class EmailAuthenticationForm(AuthenticationForm):
    """Форма аутентификации  по электронной почте."""
    username = forms.EmailField(
        label="Электронная почта",
        max_length=254,
        help_text="Введите ваш email",
    )
