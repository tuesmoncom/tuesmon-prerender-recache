from django.apps import AppConfig


class PrerenderRecacheAppConfig(AppConfig):
    name = "prerender_recache"
    verbose_name = "Prerender recache config"

    def ready(self):
        from . import signals
