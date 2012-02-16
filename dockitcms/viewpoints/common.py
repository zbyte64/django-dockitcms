from dockitcms.models import ViewPoint, Collection

import dockit

class BaseCollectionViewPoint(ViewPoint):
    collection = dockit.ReferenceField(Collection)
    
    class Meta:
        proxy = True

