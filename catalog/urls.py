from django.urls import path

from catalog import views

urlpatterns = [
    path("", views.home, name="home"),
    path("contacts/", views.contacts, name="contacts"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
    path("add/", views.add_product, name="add_product"),
]
