from django.dispatch import Signal

reload_site = Signal(providing_args=["cms_site"])
pre_init_applications = Signal(providing_args=["cms_site"])
post_init_applications = Signal(providing_args=["cms_site"])
post_reload_site = Signal(providing_args=["cms_site"])

