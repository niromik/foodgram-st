from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.base import RedirectView

from core.models import CulinaryRecipe


class ShortRedirectView(RedirectView):
    """
    Обработчик редиректа для коротких ссылок рецептов.

    Конвертирует HEX-идентификатор в числовой ID рецепта и перенаправляет
    на полную страницу рецепта. Если рецепт не найден - перенаправляет на 404.
    """

    permanent = False

    def get_redirect_url(self, short_link):
        """Генерация URL для перенаправления."""
        try:
            recipe_id = int(short_link, 16)
            get_object_or_404(CulinaryRecipe, id=recipe_id)
            return f'/recipes/{recipe_id}'
        except (Http404, ValueError):
            return '/404'
