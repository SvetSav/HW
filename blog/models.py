from django.db import models


class BlogPost(models.Model):
    title = models.CharField(max_length=200, verbose_name="заголовок")
    content = models.TextField(verbose_name="содержимое")
    preview = models.ImageField(
        upload_to="blog/", blank=True, null=True, verbose_name="превью"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="дата создания")
    is_published = models.BooleanField(default=True, verbose_name="опубликовано")
    views_count = models.PositiveIntegerField(
        default=0, verbose_name="количество просмотров"
    )

    class Meta:
        verbose_name = "блоговая запись"
        verbose_name_plural = "блоговые записи"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
