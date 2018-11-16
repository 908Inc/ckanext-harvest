from ckan.controllers.package import PackageController
from ckan.common import c
from ckan.lib.base import abort


class SourceController(PackageController):
    def new(self, data=None, errors=None, error_summary=None):
        if not c.userobj or not c.userobj.sysadmin:
            abort(404)
        return super(SourceController, self).new(data, errors, error_summary)

    def show_deleted(self):
        return 'DELETED'
