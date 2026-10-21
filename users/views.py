from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import EmailAuthenticationForm, UserProfileForm, UserRegisterForm
from .models import User


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        response = super().form_valid(form)
        # Автоматический вход после регистрации
        login(self.request, self.object)
        # Приветственное письмо
        send_mail(
            subject="Добро пожаловать в Skystore!",
            message=(
                f"Здравствуйте!\n\n"
                f"Спасибо за регистрацию на Skystore с email {self.object.email}.\n"
                f"Теперь вы можете добавлять и редактировать товары.\n\n"
                f"С уважением, команда Skystore."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.object.email],
            fail_silently=True,
        )
        return response


class EmailLoginView(LoginView):
    template_name = "users/login.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True


class Logout(LogoutView):
    next_page = reverse_lazy("home")


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "users/profile.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user
