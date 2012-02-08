from django.utils.text import capfirst

from admin_tools.dashboard.modules import DashboardModule

from dockitcms.models import Collection

class CollectionList(DashboardModule):
    template = 'admin_tools/dashboard/modules/model_list.html'
    
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
            item = {'title':title,
                    'change_url':url,
                    'add_url':url+'add/',}
            self.children.append(item)
        self._init = True
    
    def is_empty(self):
        return len(self.children) == 0

