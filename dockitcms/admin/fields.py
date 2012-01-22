from django.utils.encoding import force_unicode
from django.utils.html import escape

from dockit.admin.fields import DotPathField, DotPathWidget

from dockitcms.common import REGISTERED_VIEW_POINTS
from dockitcms.properties import GenericViewPointEntryField

from urllib import urlencode

class ViewPointEntryWidget(DotPathWidget):
    input_type = 'submit'
    
    def __init__(self, dotpath=None):
        self.dotpath = dotpath
        super(DotPathWidget, self).__init__()
    
    def render_type_dropdown(self, dotpath):
        options = list()
        for key, view_class in REGISTERED_VIEW_POINTS.iteritems():
            options.append(u'<option value="%s">%s</option>' % (key, escape(force_unicode(view_class.label))))
        data = {'next_dotpath':dotpath,
                'name':'view_type',}
        name = '[fragment-passthrough]%s' % urlencode(data)
        return u'<select name="%s">%s</select>' % (name, '\n'.join(options))
    
    def get_label(self, dotpath, value=None):
        if value:
            return escape(force_unicode(value))
        return self.render_type_dropdown(dotpath)

class ViewPointEntryField(DotPathField):
    widget = ViewPointEntryWidget

