from django.core.urlresolvers import get_resolver, get_urlconf

from dockitcms.signals import reload_site, post_reload_site


def kick_off_reload_site(cms_site, **kwargs):
    cms_site.reload_site()
reload_site.connect(kick_off_reload_site)

def refresh_resolver(resolver=None, **kwargs):
    if resolver is None:
        urlconf = get_urlconf()
        resolver = get_resolver(urlconf)
    #TODO test how this effects current requests
    resolver._populate()
post_reload_site.connect(refresh_resolver)
