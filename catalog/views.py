from django.shortcuts import render

from .models import Contact, Product  # ← добавьте обе модели


def home(request):
    """Главная страница с каталогом"""
    latest_products = Product.objects.order_by("-created_at")[:5]
    print("Последние 5 продуктов:", latest_products)
    return render(request, "catalog/home.html")


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
