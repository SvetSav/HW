from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from blog.models import BlogPost
from catalog.models import Product


class Command(BaseCommand):
    help = 'Создаёт группы "Модератор продуктов" и "Контент-менеджер" с нужными правами'

    def handle(self, *args, **options):
        # --- Модератор продуктов ---
        product_ct = ContentType.objects.get_for_model(Product)
        unpublish_perm, _ = Permission.objects.get_or_create(
            codename="can_unpublish_product",
            content_type=product_ct,
            defaults={"name": "Может отменять публикацию продукта"},
        )
        delete_product_perm = Permission.objects.get(
            codename="delete_product", content_type=product_ct
        )

        moderators, _ = Group.objects.get_or_create(name="Модератор продуктов")
        moderators.permissions.set([unpublish_perm, delete_product_perm])
        self.stdout.write(
            self.style.SUCCESS(
                f'Группа "{moderators.name}" готова: {[p.codename for p in moderators.permissions.all()]}'
            )
        )

        # --- Контент-менеджер (доп. задание) ---
        blog_ct = ContentType.objects.get_for_model(BlogPost)
        blog_perms = Permission.objects.filter(
            content_type=blog_ct,
            codename__in=[
                "add_blogpost",
                "change_blogpost",
                "delete_blogpost",
                "view_blogpost",
            ],
        )
        content_managers, _ = Group.objects.get_or_create(name="Контент-менеджер")
        content_managers.permissions.set(blog_perms)
        self.stdout.write(
            self.style.SUCCESS(
                f'Группа "{content_managers.name}" готова: {[p.codename for p in blog_perms]}'
            )
        )
