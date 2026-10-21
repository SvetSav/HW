from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from .forms import ProductForm
from .models import Category, Contact, Product
from .services import get_products_by_category


@method_decorator(cache_page(60 * 15), name="dispatch")  # 15 минут
class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"


class HomeView(ListView):
    model = Product
    template_name = "catalog/home.html"
    context_object_name = "products"
    paginate_by = 3

    def get_queryset(self):
        # На главной показываем только опубликованные продукты
        return Product.objects.filter(is_published=True).order_by("-created_at")


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"


class ContactsView(TemplateView):
    template_name = "catalog/contacts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contacts"] = Contact.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        # Обработка формы обратной связи
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        message = request.POST.get("message")
        print(f"Новое сообщение от {name} ({phone}): {message}")
        context = self.get_context_data()
        context["success"] = True
        return self.render_to_response(context)


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "catalog/add_product.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.is_published = False  # по умолчанию — не опубликован
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "catalog/add_product.html"

    def test_func(self):
        product = self.get_object()
        user = self.request.user
        return (
            user.is_superuser
            or product.owner_id == user.id
            or user.has_perm("catalog.can_unpublish_product")
        )

    def get_success_url(self):
        return reverse_lazy("product_detail", kwargs={"pk": self.object.pk})


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = "catalog/product_confirm_delete.html"
    success_url = reverse_lazy("home")

    def test_func(self):
        product = self.get_object()
        user = self.request.user
        return (
            user.is_superuser
            or product.owner_id == user.id
            or user.has_perm("catalog.can_unpublish_product")
        )


class ProductTogglePublishView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Отмена/установка публикации — только для модераторов."""

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.has_perm("catalog.can_unpublish_product")

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.is_published = not product.is_published
        product.save()
        return redirect("product_detail", pk=pk)


class CategoryProductsView(ListView):
    template_name = "catalog/category_products.html"
    context_object_name = "products"
    paginate_by = 12  # по желанию

    def get_queryset(self):
        category = get_object_or_404(Category, pk=self.kwargs["pk"])
        # Сервис уже кеширует результат по ключу category_{id}
        return get_products_by_category(category.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = get_object_or_404(Category, pk=self.kwargs["pk"])
        return context
