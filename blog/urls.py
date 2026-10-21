from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.BlogListView.as_view(), name="list"),
    path("create/", views.BlogCreateView.as_view(), name="create"),
    path("<int:pk>/", views.BlogDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.BlogUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.BlogDeleteView.as_view(), name="delete"),
]
