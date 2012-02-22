
def widgets(scope):
    if 'object' in scope.kwargs:
        obj = scope.kwargs['object']
        if hasattr(obj, 'widgets'):
            scope.add_data('widgets', obj.widgets)

