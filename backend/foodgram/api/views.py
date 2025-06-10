from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.base import RedirectView

from core.models import Recipe


class ShortRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, short_link):
        try:
            recipe_id = int(short_link, 16)
            get_object_or_404(Recipe, id=recipe_id)
            return f'/recipes/{recipe_id}'
        except (Http404, ValueError):
            return '/404'
