class SiteReloader(object):
    def signal_reload(self):
        from dockitcms.sites import site
        site.reload_site()
