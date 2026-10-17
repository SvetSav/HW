from django import forms

from .models import Category, Product

FORBIDDEN_WORDS = [
    "казино",
    "криптовалюта",
    "крипта",
    "биржа",
    "дешево",
    "бесплатно",
    "обман",
    "полиция",
    "радар",
]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "image", "category", "price"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем Bootstrap классы ко всем полям
        for field_name, field in self.fields.items():
            if isinstance(field, forms.BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if name:
            lower_name = name.lower()
            for word in FORBIDDEN_WORDS:
                if word in lower_name:
                    raise forms.ValidationError(
                        f'Название содержит запрещённое слово: "{word}"'
                    )
        return name

    def clean_description(self):
        description = self.cleaned_data.get("description")
        if description:
            lower_desc = description.lower()
            for word in FORBIDDEN_WORDS:
                if word in lower_desc:
                    raise forms.ValidationError(
                        f'Описание содержит запрещённое слово: "{word}"'
                    )
        return description

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is None:
            return price
        if price < 0:
            raise forms.ValidationError("Цена не может быть отрицательной.")
        return price

    # Дополнительное задание: валидация изображения
    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image:
            # Проверка размера
            if image.size > 5 * 1024 * 1024:  # 5 MB
                raise forms.ValidationError(
                    "Размер изображения не должен превышать 5 МБ."
                )
            # Проверка формата
            allowed_types = ["image/jpeg", "image/png"]
            if image.content_type not in allowed_types:
                raise forms.ValidationError(
                    "Формат изображения должен быть JPEG или PNG."
                )
        return image
