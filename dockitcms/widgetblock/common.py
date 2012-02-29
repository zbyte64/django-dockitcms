from dockit.schema.schema import create_schema

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
    
    def keys(self):
        return self.original_schemas.keys()
