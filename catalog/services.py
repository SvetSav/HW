from django.core.cache import cache

from .models import Product

CATEGORY_PRODUCTS_TTL = 300  # 5 минут


def get_products_by_category(category_id: int):
    """
    Возвращает список продуктов в указанной категории.
    Сначала проверяет Redis по ключу category_{id}; если нет — запрашивает БД
    и сохраняет результат в кеш на CATEGORY_PRODUCTS_TTL секунд.
    """
    cache_key = f"category_{category_id}"
    products = cache.get(cache_key)

    if products is None:
        # Кеш-промах: достаём из БД
        products = list(
            Product.objects.filter(category_id=category_id)
            .select_related("category")
            .order_by("-created_at")
        )
        cache.set(cache_key, products, timeout=CATEGORY_PRODUCTS_TTL)

    return products
