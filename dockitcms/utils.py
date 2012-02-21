from django.template import Context
from django.template.loader import get_template

def _generate_context_for_scaffold(document):
    context = {'document':document,
               'fields':document._meta.fields,
               'lflt':'{{',
               'rflt':'}}',
               'ltag':'{%',
               'rtag':'%}',}
    return context

def generate_object_list_scaffold(document):
    context = _generate_context_for_scaffold(document)
    template = get_template('dockitcms/scaffold/object_list.html')
    return template.render(Context(context))

def generate_object_detail_scaffold(document):
    context = _generate_context_for_scaffold(document)
    template = get_template('dockitcms/scaffold/object_detail.html')
    return template.render(Context(context))

def prep_for_kwargs(dictionary):
    if hasattr(dictionary, 'to_primitive'):
        return dictionary.to_primitive(dictionary)
    result = dict()
    for key, value in dictionary.iteritems():
        result[str(key)] = value
    return result

