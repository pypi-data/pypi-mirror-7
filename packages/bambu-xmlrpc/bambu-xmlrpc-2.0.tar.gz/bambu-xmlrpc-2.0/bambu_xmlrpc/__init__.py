from django.template.response import TemplateResponse
from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
from xmlrpclib import Fault

__version__ = '2.0'
dispatcher = SimpleXMLRPCDispatcher(
    allow_none = False, encoding = None
)

def handler(namespace = ''):
    """
    A decorator that turns a normal Python function into a Django-aware view that conforms to the
    XML-RPC spec
    
    :param namespace: The fully-qualified namespace for the function
    """
    
    def _decorator(func):
        dispatcher.register_function(func,
            namespace or '%s.%s' % (func.__module__, func.__name__)
        )
        
        return func
    return _decorator

def autodiscover():
    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule
    
    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        
        try:
            import_module('%s.xmlrpc' % app)
        except:
            if module_has_submodule(mod, 'xmlrpc'):
                raise

class XMLRPCException(Fault):
    def __init__(self, message, code = 0, *args, **kwargs):
        Fault.__init__(self, code, message, *args, **kwargs)