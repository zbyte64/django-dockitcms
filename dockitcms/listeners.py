from dockitcms.signals import reload_site

def kick_off_reload_site(cms_site, **kwargs):
    cms_site.reload_site()
reload_site.connect(kick_off_reload_site)
