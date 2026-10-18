from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class UserRegisterForm(UserCreationForm):
    """Форма регистрации с подтверждением пароля (password1 и password2 есть в UserCreationForm)."""

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "you@example.com"}
        ),
    )

    class Meta:
        model = User
        fields = ("email",)
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Стилизуем поля паролей
        for name in ("password1", "password2"):
            self.fields[name].widget.attrs["class"] = "form-control"
        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Подтверждение пароля"


class EmailAuthenticationForm(AuthenticationForm):
    """Форма входа по email (username в AuthenticationForm = email в нашей модели)."""

    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "you@example.com",
                "autofocus": True,
            }
        ),
    )
    password = forms.CharField(
        label="Пароль", widget=forms.PasswordInput(attrs={"class": "form-control"})
    )


class UserProfileForm(forms.ModelForm):
    """Редактирование профиля (дополнительное задание)."""

    class Meta:
        model = User
        fields = ("email", "avatar", "phone", "country")
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "avatar": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.TextInput(attrs={"class": "form-control"}),
        }
