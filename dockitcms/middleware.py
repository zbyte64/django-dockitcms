from scope import get_site_scope, Scope

class DefaultScopeMiddleware(object):
    def process_template_response(self, request, response):
        if hasattr(response, 'context_data') and response.context_data is not None: #TODO this shouldn't happen
            context = response.context_data
            if 'scopes' not in context:
                context['scopes'] = [get_site_scope()]
                if 'object' in context and not any([scope.name == 'object' for scope in context['scopes']]):
                    context['scopes'].append(Scope(name='object', object=context['object']))
        return response

