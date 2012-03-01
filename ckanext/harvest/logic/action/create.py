import re

from ckan.logic import NotFound, ValidationError, check_access
from ckan.lib.navl.dictization_functions import validate

from ckanext.harvest.model import (HarvestSource, HarvestJob, HarvestObject)
from ckanext.harvest.logic.schema import harvest_source_form_schema
from ckanext.harvest.logic.dictization import (harvest_source_dictize,
                                               harvest_job_dictize)
from ckanext.harvest.logic.action.get import harvest_source_list,harvest_job_list

def harvest_source_create(context,data_dict):

    check_access('harvest_source_create',context,data_dict)

    model = context['model']
    session = context['session']

    schema = harvest_source_form_schema()
    data, errors = validate(data_dict, schema)

    if errors:
        session.rollback()
        raise ValidationError(errors,_error_summary(errors))

    source = HarvestSource()
    source.url = data['url']
    source.type = data['type']

    opt = ['active','title','description','user_id','publisher_id','config']
    for o in opt:
        if o in data and data[o] is not None:
            source.__setattr__(o,data[o])

    if 'active' in data_dict:
        source.active = data['active']

    source.save()

    return harvest_source_dictize(source,context)

def harvest_job_create(context,data_dict):

    check_access('harvest_job_create',context,data_dict)

    source_id = data_dict['source_id']

    # Check if source exists
    source = HarvestSource.get(source_id)
    if not source:
        raise NotFound('Harvest source %s does not exist' % source_id)

    # Check if the source is active
    if not source.active:
        raise Exception('Can not create jobs on inactive sources')

    # Check if there already is an unrun job for this source
    data_dict ={
        'source_id':source_id,
        'status':u'New'
    }
    exists = harvest_job_list(context,data_dict)
    if len(exists):
        raise Exception('There already is an unrun job for this source')

    job = HarvestJob()
    job.source = source

    job.save()
    return harvest_job_dictize(job,context)

def harvest_job_create_all(context,data_dict):

    check_access('harvest_job_create_all',context,data_dict)

    data_dict.update({'only_active':True})

    # Get all active sources
    sources = harvest_source_list(context,data_dict)
    jobs = []
    # Create a new job for each, if there isn't already one
    for source in sources:
        data_dict ={
            'source_id':source['id'],
            'status':u'New'
        }

        exists = harvest_job_list(context,data_dict)
        if len(exists):
            continue

        job = harvest_job_create(context,{'source_id':source['id']})
        jobs.append(job)

    return jobs

def _error_summary(error_dict):
    error_summary = {}
    for key, error in error_dict.iteritems():
        error_summary[_prettify(key)] = error[0]
    return error_summary

def _prettify(field_name):
    field_name = re.sub('(?<!\w)[Uu]rl(?!\w)', 'URL', field_name.replace('_', ' ').capitalize())
    return field_name.replace('_', ' ')

