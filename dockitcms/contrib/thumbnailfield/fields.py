from dockitcms.fields import BaseFieldEntry, ListFieldMixin

import dockit

import properties

IMAGE_FORMATS = [('JPEG', '.jpg'),
                 ('PNG', '.png'),]

CROP_CHOICES = [('smart', 'Smart'),
                ('scale', 'Scale'),]

class ThumbnailFieldEntrySchema(dockit.Schema):
    key = dockit.SlugField()
    format = dockit.CharField(blank=True, null=True, choices=IMAGE_FORMATS)
    quality = dockit.IntegerField(blank=True, null=True)
    width = dockit.IntegerField(blank=True, null=True)
    height = dockit.IntegerField(blank=True, null=True)
    upscale = dockit.BooleanField(default=False, help_text='Upsize the image if it doesn\'t match the width and height')
    crop = dockit.CharField(blank=True, null=True, choices=CROP_CHOICES)
    autocrop = dockit.BooleanField(default=False, help_text='Remove white space from around the image')
    
    def __unicode__(self):
        return self.key or repr(self)


class ThumbnailField(BaseFieldEntry):
    thumbnails = dockit.ListField(dockit.SchemaField(ThumbnailFieldEntrySchema))
    
    field_class = properties.ThumbnailField
    
    def get_field_kwargs(self):
        kwargs = super(ThumbnailField, self).get_field_kwargs()
        
        if kwargs.get('verbose_name', None) == '':
            del kwargs['verbose_name']
        thumbnails = kwargs.pop('thumbnails', list())
        config = {'thumbnails': dict()}
        for thumb in thumbnails:
            key = thumb.pop('key')
            
            for key, value in thumb.items():
                if value is None:
                    thumb.pop(key)
            
            resize = {}
            for key in ['width', 'height', 'crop', 'upscale']:
                if key in thumb:
                    resize[key] = thumb.pop(key)
            if resize:
                thumb['resize'] = resize
            config['thumbnails'][key] = thumb
        kwargs['config'] = config
        return kwargs

    class Meta:
        typed_key = 'ThumbnailField'

class ListThumbnailField(ListFieldMixin, ThumbnailField):
    def get_list_field_kwargs(self):
        subfield = ThumbnailField.create_field(self)
        return {'subfield': subfield}

    class Meta:
        typed_key = 'ListThumbnailField'

