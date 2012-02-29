from dockit import schema

from django.contrib.contenttypes.models import ContentType

class ModelFilter(schema.Schema):
    key = schema.CharField()
    value = schema.CharField()

class ModelMixin(schema.Schema):
    model = schema.ModelReferenceField(ContentType)
    inclusion_filters = schema.ListField(schema.SchemaField(ModelFilter), blank=True)
    exclusion_filters = schema.ListField(schema.SchemaField(ModelFilter), blank=True)
    
    def get_model(self):
        return self.model.model_class()
    
    def get_base_queryset(self):
        model = self.get_model()
        queryset = model.objects.all()
        inclusions = dict()
        exclusions = dict()
        for model_filter in self.inclusion_filters:
            inclusions[str(model_filter.key)] = model_filter.value
        for model_filter in self.exclusion_filters:
            exclusions[str(model_filter.key)] = model_filter.value
        
        if inclusions:
            queryset = queryset.filter(**inclusions)
        if exclusions:
            queryset = queryset.exclude(**exclusions)
        return queryset

