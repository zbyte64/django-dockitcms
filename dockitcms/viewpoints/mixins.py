from dockitcms.mixins import BaseMixin, register_mixin
from dockitcms.models import BaseViewPoint

from dockit import schema

from exceptions import HttpForbidden

class BaseViewPointMixin(BaseMixin):
    event_handlers = {}
    
    def handle_view_point_event(self, event, view, kwargs):
        '''
        event: a string clasifying the event, ie 'dispatch', 'response', 'queryset'
        kwargs: keywords args associated to the event
        '''
        if event in self.event_handlers:
            func = self.event_handlers[event]
            if isinstance(func, basestring):
                func = getattr(self, func)
            return func(event, view, **kwargs)
        return None

class AuthConfiguration(schema.Schema):
    authenticated_users_only = schema.BooleanField(default=False)
    staff_only = schema.BooleanField(default=False)
    required_permissions = schema.ListField(schema.CharField(), blank=True) #object or app permissions required for the user

class AuthMixin(BaseViewPointMixin):
    _auth = schema.SchemaField(AuthConfiguration)
    
    class MixinMeta:
        admin_display = 'inline'
    
    #view point events
    event_handlers = {
        'dispatch': 'on_dispatch',
        'object': 'on_object',
    }
    
    def on_dispatch(self, event, view, **kwargs):
        user = kwargs['request'].user
        if self._auth.authenticated_users_only and not user.is_authenticated():
            raise HttpForbidden()
        if self._auth.staff_only and not user.is_staff:
            raise HttpForbidden()
        for perm in self._auth.required_permissions:
            if not user.has_perm(perm):
                raise HttpForbidden()
    
    def on_object(self, event, view, **kwargs):
        obj = kwargs['object']
        user = view.request.user
        auth_info = getattr(obj, '_auth', None)
        required_perms = set(self._auth.required_permissions)
        
        if auth_info:
            if auth_info.authenticated_users_only and not user.is_authenticated():
                raise HttpForbidden()
            if auth_info.staff_only and not user.is_staff:
                raise HttpForbidden()
            required_perms.update(auth_info.required_permissions)
        for perm in required_perms:
            if not user.has_perm(perm, obj):
                raise HttpForbidden()
    
    def on_context(self, event, view, **kwargs):
        context = kwargs['context']
        user = view.request.user
        obj = getattr(view, 'object', None)
        context['object_user_perms'] = user.get_all_permissions(obj)

register_mixin(AuthMixin)
BaseViewPoint.register_schema_mixin(AuthMixin)

