from django.dispatch import Signal

post_api_reload = Signal(providing_args=["api_site"])
