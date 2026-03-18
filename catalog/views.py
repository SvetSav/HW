from django.shortcuts import render


def home(request):
    """Главная страница с каталогом"""
    return render(request, "catalog/home.html")


def contacts(request):
    """Страница контактов с формой обратной связи"""
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        message = request.POST.get("message")
        print(f"Новое сообщение от {name} ({phone}): {message}")
        context = {"success": True}
    else:
        context = {}
    return render(request, "catalog/contacts.html", context)
