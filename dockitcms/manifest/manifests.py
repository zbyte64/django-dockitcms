from dockit.manifest.manifests import DockitFixtureManifest
from dockit.core import serializers as dockit_serializers
from dockit import schema

class DockitCMSFixtureManifest(DockitFixtureManifest):
    '''
    Manifest to handle loading of dockitcms objects: virtual collections, indexes, view points, subsites, etc
    '''
    def load_data_sources(self, loader):
        self.subsites = self.parse_data_sources(loader, self.options['subsites'])
        self.applications = self.parse_data_sources(loader, self.options['applications'])
        self.collections = self.parse_data_sources(loader, self.options['collections'])
        self.collection_data = dict()
        for key, value in self.options['collection_data'].iteritems():
            data_source = self.parse_data_sources(loader, value)
            self.collection_data[key] = data_source
        self.viewpoints = self.parse_data_sources(loader, self.options['viewpoints'])
        self.indexes = self.parse_data_sources(loader, self.options['indexes'])
        self.documentdesign = self.parse_data_sources(loader, self.options['documentdesign'])
    
    def load(self, include_data=True, existing_object_map=None, skip_collection_data=None, conserve_indexes=True, rename_collections=None):
        '''
        existing_object_map = {
            'collection': {
                <natural_key>: <object>
            }
        }
        
        rename_collections = {
            'team': 'dev.team',
            'teammember': 'dev.teammember',
        }
        
        skip_collection_data = [collectionkey1, collectionkey2]
        
        #rename/replace applications & subsites through existing_object_map (you need to create the app & subsite yourself)
        #conserve_indexes: indexes attempt to do functional mapping, ie avoid duplicate indexes
        '''
        self.existing_object_map = existing_object_map or dict()
        
        #normalize existing object map
        for key, value in self.existing_object_map.items():
            if isinstance(value, (list, tuple)):
                new_value = dict()
                for skey, svalue in value:
                    skey = self._hashable(skey)
                    new_value[skey] = svalue
                self.existing_object_map[key] = new_value
        
        self.rename_collections = rename_collections or dict()
        self.conserve_indexes = conserve_indexes
        self._loaded_collections = dict()
        results = list()
        
        results.extend(self.load_from_data_sources(self.subsites))
        results.extend(self.load_from_data_sources(self.applications))
        results.extend(self.load_from_data_sources(self.documentdesign))
        results.extend(self.load_from_data_sources(self.collections))
        
        results.extend(self.load_from_data_sources(self.indexes))
        
        if include_data:
            for key, data_source in self.collection_data.iteritems():
                if skip_collection_data and key in skip_collection_data:
                    continue
                #if key in self.rename_collections
                results.extend(self.load_from_data_sources(data_source))
        
        results.extend(self.load_from_data_sources(self.viewpoints))
        return results
    
    def save_object(self, obj):
        #if object in existing_object_map, return None
        #then resolve/hijack key relations
        
        if self._object_in_object_map(obj.object, self.existing_object_map):
            return
        
        self._process_object_through_object_map(obj.object, self.existing_object_map)
        
        #CONSIDER collection.key is optional; 
        if obj.object._meta.collection == 'dockitcms.basecollection':
            if obj.object.key in self.rename_collections:
                original_key = obj.object.key
                original_map_key = self._get_object_key(obj)
                obj.object.key = self.rename_collections[original_key]
                
                #TODO this should not be necessary
                obj.object._primitive_data.pop('@natural_key', None)
                obj.object._primitive_data.pop('@natural_key_hash', None)
                obj.natural_key = obj.object.create_natural_key()
                
                #update existing object map so future indexes point to this
                self._add_to_object_map(obj.object, original_map_key, obj.natural_key)
            self._loaded_collections[obj.object.key] = obj.object
        
        if self.conserve_indexes and obj.object._meta.collection == 'dockitcms.indexes':
            existing_index = self._lookup_comparable_index(obj.object)
            if existing_index:
                #we've found an index that matches, update object map
                self._add_to_object_map(existing_index)
                return existing_index
            #if renaming a collection, object map should have taken care of the details
        
        if obj.object._meta.collection.startswith('dockitcms.virtual.'):
            collection_key = obj.object._meta.collection[len('dockitcms.virtual.'):]
            if collection_key in self.rename_collections:
                #change the taget collection by loading it into our mapped collection
                new_collection_key = self.rename_collections[collection_key]
                v_collection = self._loaded_collections[new_collection_key]
                document_cls = v_collection.get_document()
                primitive_data = obj.object.to_portable_primitive(obj.object)
                obj.object = document_cls.from_portable_primitive(primitive_data)
        
        obj.save()
        
        return obj.object
    
    def _hashable(self, val):
        if isinstance(val, dict):
            return tuple(val.items())
        if isinstance(val, list):
            return tuple(val)
        return val
    
    def _get_object_key(self, obj):
        if hasattr(obj, 'natural_key_hash'):
            return obj.natural_key_hash
        elif hasattr(obj, 'natural_key'):
            key = obj.natural_key
            if callable(key):
                key = key()
            return self._hashable(key)
        else:
            return obj.pk
    
    def _add_to_object_map(self, obj, *extra_keys):
        all_keys = list(extra_keys)
        all_keys.append(self._get_object_key(obj))
        collection = obj._meta.collection
        self.existing_object_map.setdefault(collection, {})
        for key in all_keys:
            self.existing_object_map[collection][self._hashable(key)] = obj
    
    def _lookup_comparable_index(self, obj):
        #TODO match obj index to others in the system.
        #assume obj has already been processed through object map
        return False
    
    def _process_object_through_object_map(self, obj, existing_object_map):
        #CONSIDER: there may be deep, deep relations: schema should have a method to recursively set a natural key map
        #CONSIDER: reference fields could use dictionaries in place of keys
        for name, field in obj._meta.fields.iteritems():
            #TODO proper check iterable types
            if hasattr(field, 'subfield'): #likely an iterable
                values_list = getattr(obj, name, None)
                if values_list is None:
                    continue
                if isinstance(field.subfield, schema.SchemaField):
                    for val in values_list:
                        self._process_object_through_object_map(val, existing_object_map)
                elif isinstance(field.subfield, schema.ReferenceField):
                    new_val = list()
                    for val in values_list: #TODO operate on raw value from the dump
                        key = self._get_object_key(val)
                        replacement = existing_object_map.get(val._meta.collection, {}).get(key, None)
                        new_val.append(replacement)
                    setattr(obj, name, new_val)
                
            elif isinstance(field, schema.SchemaField): 
                val = getattr(obj, name, None)
                if val is not None:
                    self._process_object_through_object_map(val, existing_object_map)
            elif isinstance(field, schema.ReferenceField):
                #CONSIDER: we should operate on the raw value supplied from the dump
                #val = getattr(obj, name, None)
                key = obj._primitive_data.get(name, None)
                collection = field.document._meta.collection
                if key is not None:
                    #key = self._get_object_key(val)
                    key = self._hashable(key)
                    replacement = existing_object_map.get(collection, {}).get(key, None)
                    if replacement is not None:
                        setattr(obj, name, replacement)
    
    def _object_in_object_map(self, obj, existing_object_map):
        natural_key = self._get_object_key(obj)
        existing_obj = existing_object_map.get(obj._meta.collection, {}).get(natural_key, None)
        if existing_obj is not None:
            return True
        return False
    
    @classmethod
    def dump(cls, objects, data_source, data_source_key, **options):
        subsites = list()
        applications = list()
        collections = list()
        collection_data = dict()
        viewpoints = list()
        indexes = list()
        documentdesign = list()
        
        from dockitcms import models
        
        for obj in objects:
            if isinstance(obj, models.Subsite):
                subsites.append(obj)
            elif isinstance(obj, models.Application):
                applications.append(obj)
            elif isinstance(obj, models.DocumentDesign):
                documentdesign.append(obj)
            elif isinstance(obj, models.BaseCollection):
                collections.append(obj)
            elif isinstance(obj, models.BaseViewPoint):
                viewpoints.append(obj)
            elif isinstance(obj, models.BaseIndex):
                indexes.append(obj)
            elif obj._meta.collection.startswith('dockitcms.virtual.'):
                key = obj._meta.collection[len('dockitcms.virtual.'):]
                collection_data.setdefault(key, list())
                collection_data[key].append(obj)
            else:
                assert False, "Unhandled object %s" % obj
            pass #TODO route the object to the proper destination
        
        def prep_data(data):
            prep_data = dockit_serializers.serialize('python', data)
            results = data_source.to_payload(data_source_key, prep_data, **options)
            return [results]
        
        subsites = prep_data(subsites)
        applications = prep_data(applications)
        collections = prep_data(collections)
        for key, values in collection_data.items():
            collection_data[key] = prep_data(values)
        viewpoints = prep_data(viewpoints)
        indexes = prep_data(indexes)
        documentdesign = prep_data(documentdesign)
        
        results = {
            'documentdesign': documentdesign,
            'collections': collections,
            'collection_data': collection_data,
            'indexes': indexes,
            'viewpoints': viewpoints,
            'subsites': subsites,
            'applications': applications,
        }
        
        return results

'''
{'loader':'dockitcmsfixture',
 'references': {
    'applications': [app_nkey1, app_nkey2] #defines app references by natural keys
    'subsites': [subsite_nkey1, subsite_nkey2] #includes referenced subsites
    #CONSIDER: indexes do not have natural keys, but is not needed as we can look for functional equivalence
    #a special loader can read this info and offer the user to define their own mappings
 },
 'documentdesign': [#data sources],
 'collections': [#data sources], 
 'collection_data': {
    'collection_nkey1':[#data sources],
    'collection_nkey2':[#data sources],
 }
 'indexes': [#data sources],
 'viewpoints': [#data sources],
 'subsites': [#data sources],
 'applications': [#data sources],
}
'''

