from dockit import schema

import os

from django.core.files.base import ContentFile

from photoprocessor.utils import img_to_fobj
from photoprocessor.processors import process_image, process_image_info
from photoprocessor.lib import Image

class GeneratedThumbnailSchema(schema.Schema):
    image = schema.FileField()
    info = schema.DictField()
    config = schema.DictField()
    
    @property
    def url(self):
        if self.image:
            return self.image.url
    
    @property
    def width(self):
        return self.info['width']
    
    @property
    def height(self):
        return self.info['height']
    
    def __unicode__(self):
        if self.image:
            return self.image.name
        return repr(self)

class ThumbnailsSchema(GeneratedThumbnailSchema):
    thumbnails = schema.DictField(value_subfield=schema.SchemaField(GeneratedThumbnailSchema))
    
    def pil_image(self):
        file_obj = self.image
        file_obj.open()
        file_obj.seek(0)
        try:
            return Image.open(file_obj)
        except IOError:
            file_obj.seek(0)
            cf = ContentFile(file_obj.read())
            return Image.open(cf)
    
    def reprocess_info(self, config):
        source_image = self.pil_image()
        self.info = process_image_info(source_image)
        self.config = config
    
    def reprocess_thumbnail_info(self, config):
        source_image = self.pil_image()
        for key, thumbnail in self.thumbnails.iteritems():
            if key in config['thumbnails']:
                cfg = config['thumbnails'][key]
                info = process_image_info(source_image, cfg)
                thumbnail.info = info
    
    def reprocess_thumbnails(self, config, force_reprocess=False):
        base_name, base_ext = os.path.splitext(os.path.basename(self.image.name))
        source_image = self.pil_image()
        for key, cfg in config['thumbnails'].iteritems():
            if not force_reprocess and key in self.thumbnails and self.thumbnails[key].config == cfg:
                continue
            thumb_name = '%s-%s%s' % (base_name, key, base_ext)
            self.thumbnails[key] = self._process_thumbnail(source_image, thumb_name, cfg)
    
    def reprocess(self, config, force_reprocess=False):
        self.reprocess_info(config)
        self.reprocess_thumbnails(config, force_reprocess=force_reprocess)
    
    def _process_thumbnail(self, source_image, thumb_name, config):
        img, info = process_image(source_image, config)
        
        image_field = self._meta.fields['image']
        storage = image_field.storage
        
        thumb_name = storage.get_available_name(thumb_name)
        #not efficient, requires image to be loaded into memory
        thumb_fobj = ContentFile(img_to_fobj(img, info).read())
        thumb_name = storage.save(thumb_name, thumb_fobj)
        
        return GeneratedThumbnailSchema(**{'image':thumb_name, 'config':config, 'info':info})

assert hasattr(ThumbnailsSchema, 'url')

import fields
