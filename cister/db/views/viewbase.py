from cister.db.views.mixin import PermissionMixin


class BaseCisterView(PermissionMixin):


    def __init__(self, request):
        self.request = request

    def __call__(self):
        return {}
