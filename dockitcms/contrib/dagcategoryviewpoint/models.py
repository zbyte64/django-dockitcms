from django.db import models

from dagcategory.models import DAGCategory

import datetime

import dockit

from dockitcms.properties import REGISTERED_BASE_SCHEMA_DESIGNS

class DocumentCategoryManager(models.Manager):
    def listed(self):
        return self.filter(listed=True)
    
    def create_or_update_for_document(self, document):
        collection = document._meta.collection
        document_id = document.pk
        parent = None
        if document.parent:
            parent = self.create_or_update_for_document(document.parent)
        defaults = {'slug':document.slug,
                    'parent':parent,
                    'path':'',
                    'order':document.order,
                    'staff_only':document.staff_only,
                    'authenticated_users_only':document.authenticated_users_only,
                    'listed':document.listed,}
        obj, created = self.get_or_create(collection=collection, 
                                          document_id=document_id,
                                          defaults=defaults)
        if created:
            obj.save() #TODO if we compute the path properly in default this will not be necesssary
        else:
            updated = False
            for key, value in defaults.iteritems():
                if getattr(obj, key) != value:
                    setattr(obj, key, value)
                    updated = True
            if updated:
                obj.save()
        document.path = obj.path
        return obj
    
    def delete_for_document(self, document):
        collection = document._meta.collection
        document_id = document.pk
        self.filter(collection=collection, doucment_id=document_id).delete()

class DocumentCategoryModel(DAGCategory):
    collection = models.CharField(max_length=128, db_index=True)
    document_id = models.CharField(max_length=128, db_index=True)
    
    created = models.DateTimeField(default=datetime.datetime.now, editable=False)
    order = models.IntegerField(default=0)

    #visibility flags    
    staff_only = models.BooleanField(default=False)
    authenticated_users_only = models.BooleanField(default=False)
    listed = models.BooleanField(default=True, db_index=True)
    
    objects = DocumentCategoryManager()
    
    class Meta:
        ordering = ['order']

class AbstractDocumentCategory(dockit.Document):
    '''
    Inherited by other documents, on save and delete a category model is updated
    '''
    slug = dockit.SlugField()
    parent = dockit.ReferenceField('self', blank=True, null=True)
    path = dockit.CharField(editable=False)
    order = dockit.IntegerField(default=0)
    
    staff_only = dockit.BooleanField(default=False)
    authenticated_users_only = dockit.BooleanField(default=False)
    listed = dockit.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            #can only proceed if we have a document id
            super(AbstractDocumentCategory, self).save(*args, **kwargs)
        DocumentCategoryModel.objects.create_or_update_for_document(self)
        ret = super(AbstractDocumentCategory, self).save(*args, **kwargs)
        return ret
    
    def delete(self, *args, **kwargs):
        DocumentCategoryModel.objects.delete_for_document(self)
        return super(AbstractDocumentCategory, self).delete(*args, **kwargs)
    
    class Meta:
        virtual = True

REGISTERED_BASE_SCHEMA_DESIGNS['dagcategory.category'] = AbstractDocumentCategory

import categoryviewpoints

