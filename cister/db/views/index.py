from pyramid.renderers import get_renderer
from cister.db.views import BaseCisterView

class IndexView(BaseCisterView):


    def __init__(self, request):
        self.request = request

    def __call__(self):
        return {}

class NotFoundView(BaseCisterView):
    pass

class UnauthroziedView():
    def __init__(self, message, request):
        self.message = message
        self.request = request

    def __call__(self):
        #Unauthorized
        import pdb; pdb.set_trace()
        return {'message':self.message}

class ForbiddenView():
    def __init__(self, message):
        self.message = message

    def __call__(self):
        #Forbidden
        import pdb; pdb.set_trace()
        return {}
