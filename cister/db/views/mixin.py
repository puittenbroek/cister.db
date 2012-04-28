from pyramid.security import has_permission

class PermissionMixin(object):


    def news_editor(self):
        return has_permission('edit_news', self.request.context, self.request).boolval

    
    def in_manage_settings_group(self):

        return has_permission('manage_settings', self.request.context, self.request).boolval

    def in_manage_group(self):

        return has_permission('admin_view', self.request.context, self.request).boolval

