from django.core.urlresolvers import get_resolver, get_urlconf, clear_url_caches, RegexURLResolver

from dockitcms.signals import request_reload_site, post_reload_site
from dockitcms.loading import get_site_reloader


def kick_off_reload_site(**kwargs):
    get_site_reloader().request_reload()
request_reload_site.connect(kick_off_reload_site)

def refresh_resolver(resolver):
    old_namespace_dict = resolver.namespace_dict
    seen = set()
    for namespace, (regexp, regexurlpattern) in resolver.namespace_dict.iteritems():
        refresh_resolver(resolver=regexurlpattern)
        seen.add(regexurlpattern)
    for pattern in resolver.url_patterns:
        if pattern in seen:
            continue
        if isinstance(pattern, RegexURLResolver):
            refresh_resolver(resolver=pattern)
            seen.add(pattern)
    resolver._populate()

def refresh_urls(**kwargs):
    urlconf = get_urlconf()
    resolver = get_resolver(urlconf)
    refresh_resolver(resolver)
    
    clear_url_caches()

post_reload_site.connect(refresh_urls)
