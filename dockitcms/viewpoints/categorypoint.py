from dockitcms.models import ViewPoint, Collection

import dockit

class CategoryViewPoint(ViewPoint):
    category_collection = dockit.ReferenceField(Collection)
    category_slug_field = dockit.CharField()
    
    item_collection = dockit.ReferenceField(Collection)
    item_slug_field = dockit.CharField()
    
    item_category_dot_path = dockit.CharField()
    
    class Meta:
        typed_key = 'categoryview'
