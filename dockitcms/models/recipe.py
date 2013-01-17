from dockit import schema

from dockitcms.models.collection import Collection, Application
from dockitcms.models.view_point import BaseViewPoint, Subsite
from dockitcms.models.index import Index

class BaseRecipe(schema.Document):
    #fields to keep track of what the recipe generated
    generated_applications = schema.ListField(schema.ReferenceField(Application), editable=False)
    generated_collections = schema.ListField(schema.ReferenceField(Collection), editable=False)
    generated_indexes = schema.ListField(schema.ReferenceField(Index), editable=False)
    #generated_view_points = schema.ListField(schema.ReferenceField(BaseViewPoint), editable=False)
    generated_subsites = schema.ListField(schema.ReferenceField(Subsite), editable=False)
    
    class Meta:
        typed_field = 'recipe_type'
        verbose_name = 'Recipe'
        collection = 'dockitcms.recipe'
    
    def cook_recipe(self):
        raise NotImplementedError #build out apps, collections and such here
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.cook_recipe()
        return super(BaseRecipe, self).save(*args, **kwargs)

class Recipe(BaseRecipe): #represents typical recipe design pattern; creates an app and attaches view points to an existing subsite
    application_name = schema.CharField() #name of app to create
    subsite = schema.ReferenceField(Subsite)
    
    def get_application_kwargs(self):
        return {'name': self.application_name}
    
    def create_application(self):
        application = Application(**self.get_application_kwargs())
        application.save()
        self.generated_applications.append(application)
    
    def get_view_point_kwargs(self):
        return {'subsite': self.subsite}
    
    def get_collection_kwargs(self):
        return {'application': self.applications[0],
                'admin_options': {'list_per_page':100},}
    
    class Meta:
        proxy = True

