from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .models import BlogPost


class BlogListView(ListView):
    model = BlogPost
    template_name = "blog/blog_list.html"
    context_object_name = "object_list"

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True)


class BlogDetailView(DetailView):
    model = BlogPost
    template_name = "blog/blog_detail.html"
    context_object_name = "post"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        old_views = obj.views_count
        obj.views_count += 1
        obj.save()
        # Проверяем, достиг ли счетчик 100
        if old_views < 100 and obj.views_count >= 100:
            send_mail(
                "Статья набрала 100 просмотров!",
                f'Статья "{obj.title}" достигла 100 просмотров.',
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=True,
            )
        return obj


class BlogCreateView(CreateView):
    model = BlogPost
    fields = ["title", "content", "preview", "is_published"]
    template_name = "blog/blog_form.html"
    success_url = reverse_lazy("blog:list")


class BlogUpdateView(UpdateView):
    model = BlogPost
    fields = ["title", "content", "preview", "is_published"]
    template_name = "blog/blog_form.html"

    def get_success_url(self):
        return reverse_lazy("blog:detail", kwargs={"pk": self.object.pk})


class BlogDeleteView(DeleteView):
    model = BlogPost
    template_name = "blog/blog_confirm_delete.html"
    success_url = reverse_lazy("blog:list")
