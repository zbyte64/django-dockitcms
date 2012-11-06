from dockitcms.resources.common import CMSDocumentResource

from hyperadmin.resources.models.models import ModelResource as BaseModelResource

class VirtualDocumentResource(CMSDocumentResource):
    pass
    #app_name
    #TODO #def get_indexes(self) => VirtualDocumentIndex

class ModelResource(BaseModelResource):
    pass
    #TODO #def get_indexes(self) => ModelIndex

