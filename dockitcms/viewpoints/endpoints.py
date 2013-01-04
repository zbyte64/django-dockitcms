from dockitcms.resources.public import PublicEndpoint


class BaseViewPointEndpoint(PublicEndpoint):
    configuration = None

class ListEndpoint(BaseViewPointEndpoint):
    pass

class DetailEndpoint(BaseViewPointEndpoint):
    pass
