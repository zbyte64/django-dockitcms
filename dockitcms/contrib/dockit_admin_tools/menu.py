from django.utils.text import capfirst

from admin_tools.menu.items import MenuItem

from dockitcms.models import Collection, Application

class CollectionList(MenuItem):
    def __init__(self, title=None, models=None, exclude=None, **kwargs):
        """
        ``CollectionList`` constructor.
        """
        self.models = list(models or [])
        self.exclude = list(exclude or [])
        self._init = False
        super(CollectionList, self).__init__(title, **kwargs)

    def init_with_context(self, context):
        if self._init:
            return
        items = Collection.objects.all()
        for collection in items:
            if collection.key in self.exclude:
                continue
            title = capfirst(collection.title)
            url = collection.get_admin_manage_url()
            item = MenuItem(title=title, url=url)
            self.children.append(item)
        self._init = True

    def is_empty(self):
        return len(self.children) == 0

class ApplicationList(MenuItem):
    def __init__(self, title=None, models=None, exclude=None, **kwargs):
        """
        ``CollectionList`` constructor.
        """
        self.title = title
        self.models = list(models or [])
        self.exclude = list(exclude or [])
        self._init = False
        super(ApplicationList, self).__init__(title, **kwargs)

    def init_with_context(self, context):
        if self._init:
            return
        items = Application.objects.all()
        collections = Collection.objects.all()
        for application in items:
            #if application.key in self.exclude:
            #    continue
            title = capfirst(application.name)
            #url = collection.get_admin_manage_url()
            item = MenuItem(title=title)
            #TODO this is not efficient
            for collection in collections:
                if collection.application == application:
                    item.children.append(self.create_menu_item_for_collection(collection))
            self.children.append(item)
        self._init = True
    
    def create_menu_item_for_collection(self, collection):
        title = capfirst(collection.title)
        url = collection.get_admin_manage_url()
        return MenuItem(title=title, url=url)
    
    def is_empty(self):
        return len(self.children) == 0

