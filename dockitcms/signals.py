from django.dispatch import Signal

request_reload_site = Signal()
'''
Called when the site needs to be reloaded
'''

reload_site = Signal()
'''
Sites are listeners that should reload
'''

pre_init_applications = Signal(providing_args=["cms_site"])
post_init_applications = Signal(providing_args=["cms_site"])
post_reload_site = Signal(providing_args=["cms_site"])

