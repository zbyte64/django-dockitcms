from dockit.schema.schema import create_schema

from django.template.loader import render_to_string

class ExpandedSchemas(object):
    def __init__(self, base_schema, original_schemas):
        self.base_schema = base_schema
        self.original_schemas = original_schemas
        self.schemas = dict()
    
    def __getitem__(self, key):
        if key not in self.schemas:
            schemas = self.original_schemas
            schema = schemas[key]
            block_schema = create_schema(schema.__name__, {}, parents=(self.base_schema, schema), proxy=True)
            
            #set typed_key incase if base schema overwrote it
            block_schema._meta.typed_key = schema._meta.typed_key
            block_schema._meta.typed_field = self.base_schema._meta.typed_field
            block_schema._meta.collection = self.base_schema._meta.collection
            self.schemas[key] = block_schema
        return self.schemas[key]
    
    def __iter__(self):
        return self.schemas.iterkeys()
    
    def keys(self):
        return self.original_schemas.keys()

class WidgetBlockScopeDisplay(object):
    template_name = 'widgetblock/scope_display.html'
    
    def __init__(self):
        self.blocks_seen = list()
    
    def render(self, context):
        return render_to_string(self.template_name, {'display':self, 'scopes':context.get('scopes', None)})
    
    def add_block(self, block_key):
        self.blocks_seen.append(block_key)
