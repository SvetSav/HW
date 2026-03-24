from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from .forms import ProductForm
from .models import Contact, Product


class HomeView(ListView):
    model = Product
    template_name = "catalog/home.html"
    context_object_name = "page_obj"  # чтобы в шаблоне осталось page_obj
    paginate_by = 3

    def get_queryset(self):
        # Сортировка по дате создания (последние сверху)
        return Product.objects.all().order_by("-created_at")


class ProductDetailView(DetailView):
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


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = "catalog/add_product.html"
    success_url = reverse_lazy("home")
