from django.db import models

from dagcategory.models import DagCategory

import datetime

import dockit

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
                    'order':document.order,
                    'staff_only':document.staff_only,
                    'authenticated_users_only':document.authenticated_users_only,
                    'listed':listed,}
        obj, created = self.get_or_create(collection=collection, 
                                          document_id=document_id,
                                          defaults=detaults)
        if not created:
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

class DocumentCategoryModel(DagCategory):
    collection = models.CharField(max_length=128, db_index=True)
    document_id = models.CharField(max_length=128, db_index=True)
    
    created = models.DateTimeField(default=datetime.now, editable=False)
    order = models.IntegerField(default=0)

    #visibility flags    
    staff_only = models.BooleanField(default=False)
    authenticated_users_only = models.BooleanField(detault=False)
    listed = models.BooleanField(default=True, db_index=True)
    
    objects = DocumentCategoryManager()
    
    def get_document(self):
        pass #TODO
    
    class Meta:
        ordering = ['order']

class AbstractDocumentCategory(dockit.Document):
    '''
    Inherited by other documents, on save and delete a category model is updated
    '''
    slug = dockit.SlugField()
    parent = dockit.RefenceField('self', blank=True, null=True)
    path = dockit.CharField(editable=False)
    order = dockit.IntegerField(default=0)
    
    staff_only = dockit.BooleanField(default=False)
    authenticated_users_only = dockit.BooleanField(detault=False)
    listed = doclit.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        DocumanteCategoryModel.objects.create_or_update_for_document(self)
        return super(AbstractDocumentCategory, self).save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        DocumanteCategoryModel.objects.delete_for_document(self)
        return super(AbstractDocumentCategory, self).delete(*args, **kwargs)
    
    class Meta:
        abstract = True

