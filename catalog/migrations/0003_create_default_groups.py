from django.db import migrations

GROUP_PERMS = {
    "Модератор продуктов": [
        ("catalog", "can_unpublish_product"),
        ("catalog", "delete_product"),
    ],
    "Контент-менеджер": [
        ("blog", "add_blogpost"),
        ("blog", "change_blogpost"),
        ("blog", "delete_blogpost"),
        ("blog", "view_blogpost"),
    ],
}


def create_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    for group_name, perms in GROUP_PERMS.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        perm_objs = []
        for app_label, codename in perms:
            ct = ContentType.objects.filter(app_label=app_label).first()
            if not ct:
                continue
            perm = Permission.objects.filter(content_type=ct, codename=codename).first()
            if perm:
                perm_objs.append(perm)
        group.permissions.set(perm_objs)


def remove_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=GROUP_PERMS.keys()).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0002_alter_product_options_product_is_published_and_more"),
        ("blog", "0001_initial"),
    ]
    operations = [
        migrations.RunPython(create_groups, remove_groups),
    ]
