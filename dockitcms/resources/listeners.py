from dockitcms.signals import reload_site
from dockitcms.resources.virtual import site

def reload_admin_site(**kwargs):
    site.reload_site()
reload_site.connect(reload_admin_site)
