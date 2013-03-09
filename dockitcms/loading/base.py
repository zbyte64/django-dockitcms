from dockitcms.signals import reload_site


class SiteReloader(object):
    def request_reload(self):
        self.signal_reload()
    
    def signal_reload(self):
        reload_site.send(sender=self)
