from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductForm
from .models import Contact, Product


def home(request):
    """Главная страница с каталогом"""
    product_list = Product.objects.all()
    paginator = Paginator(product_list, 6)  # по 6 товаров на странице
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "catalog/home.html", {"page_obj": page_obj})


def contacts(request):
    """Страница контактов с формой обратной связи"""
    contacts = Contact.objects.all()  # получаем все контакты из БД

    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        message = request.POST.get("message")
        print(f"Новое сообщение от {name} ({phone}): {message}")
        context = {"success": True, "contacts": contacts}
    else:
        context = {"contacts": contacts}

    return render(request, "catalog/contacts.html", context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "catalog/product_detail.html", {"product": product})


def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = ProductForm()
    return render(request, "catalog/add_product.html", {"form": form})
