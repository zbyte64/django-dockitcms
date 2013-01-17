from dockitcms.resources.public import PublicEndpoint

from django.template.response import TemplateResponse


class BaseViewPointEndpoint(PublicEndpoint):
    configuration = None
    
    def generate_response(self, link):
        response = super(BaseViewPointEndpoint, self).generate_response(link)
        if isinstance(response, TemplateResponse):
            response.context_data.update(self.get_context_data(self.state, link))
            response.context_data['content'] = self.view_point.render_content(response.context_data)
            response.template_name = self.view_point.get_template_names()
        return response
    
    def get_context_data(self, state, link):
        return {'resource_items':state.get_resource_items()}

class ListEndpoint(BaseViewPointEndpoint):
    def get_context_data(self, state, link):
        data = super(ListEndpoint, self).get_context_data(state, link)
        data['object_list'] = [item.instance.instance for item in state.get_resource_items()]
        return data

class DetailEndpoint(BaseViewPointEndpoint):
    def get_context_data(self, state, link):
        data = super(DetailEndpoint, self).get_context_data(state, link)
        data['object'] = state.get_resource_items()[0].instance.instance
        return data
