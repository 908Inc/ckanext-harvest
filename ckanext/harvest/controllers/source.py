from ckan.controllers.package import PackageController
from ckan.common import c
import ckan.lib.helpers as h
import ckan.plugins.toolkit as tk
from ckan.lib.base import abort

from ckanext.harvest.model import DGUAHarvesterSource


class SourceController(PackageController):
    def new(self, data=None, errors=None, error_summary=None):
        if not c.userobj or not c.userobj.sysadmin:
            abort(404)
        return super(SourceController, self).new(data, errors, error_summary)

    def show_deleted(self):
        # TODO: Access

        # sources = tk.get_action('harvest_source_list')({}, {})
        sources = [a.__dict__ for a in DGUAHarvesterSource.get_deleted_sources().all()]
        context = {
            'sources': sources
        }
        return tk.render('source/deleted_search.html', context)
