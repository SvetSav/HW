from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("contacts/", views.ContactsView.as_view(), name="contacts"),
    path("product/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("add/", views.ProductCreateView.as_view(), name="add_product"),
    path(
        "product/<int:pk>/edit/",
        views.ProductUpdateView.as_view(),
        name="product_update",
    ),
    path(
        "product/<int:pk>/delete/",
        views.ProductDeleteView.as_view(),
        name="product_delete",
    ),
    path(
        "product/<int:pk>/toggle-publish/",
        views.ProductTogglePublishView.as_view(),
        name="product_toggle_publish",
    ),
    path(
        "category/<int:pk>/products/",
        views.CategoryProductsView.as_view(),
        name="category_products",
    ),
]
