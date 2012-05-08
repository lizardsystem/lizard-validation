# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

import logging

from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext

from lizard_esf.models import Configuration
from lizard_portal.models import ConfigurationToValidate
from lizard_validation.config_comparer import ConfigComparer
from lizard_validation.config_comparer import create_wb_area_comparer
from lizard_validation.config_comparer import create_wb_bucket_comparer
from lizard_validation.config_comparer import create_wb_structure_comparer

logger = logging.getLogger(__name__)

def esf_field_translator(diff):
    """Return a copy of the dict but with the keys translated.

    Each key of the dict is the name of a DBF column, for example 'GEBIED' or
    'IN_GEBR'. Apart from that name, each column name has a human-readable
    version. This function returns a copy of the given dict that has each key
    replaced by its human-readable version. If such a version cannot be found,
    this function does not trasnslate the field name.

    """
    translated_diff = {}
    for field_name, field_value in diff.items():
        try:
            translated_field_name = \
                Configuration.objects.get(dbf_valuefield_name=field_name).name
        except Configuration.DoesNotExist:
            try:
                translated_field_name = \
                    Configuration.objects.get(dbf_manualfield_name=field_name).name + \
                    ' (handmatig)'
            except Configuration.DoesNotExist:
                translated_field_name = field_name
        translated_diff[translated_field_name] = field_value
    return translated_diff

def view_config_diff(request, area_name, config_type,
                            template='lizard_validation/config_diff.html'):
    logger.debug('lizard_validation.views.view_config_diff')
    logger.debug('look for ConfigurationToValidate for Area with name: %s',
                            area_name)
    config = get_object_or_404(ConfigurationToValidate,
        area__name=area_name, config_type=config_type)

    if config_type == 'waterbalans':

        diff = create_wb_area_comparer().compare(config)
        bucket_diff = create_wb_bucket_comparer().compare(config)
        structure_diff = create_wb_structure_comparer().compare(config)
        return render_to_response(
            'lizard_validation/wb_config_diff.html',
            { 'name': config.area.name,
              'type': config.config_type,
              'diff': diff,
              'bucket_diff': bucket_diff,
              'structure_diff': structure_diff,
              },
            context_instance=RequestContext(request))

    diff = esf_field_translator(ConfigComparer().compare(config))
    return render_to_response(
        template,
        { 'name': config.area.name,
          'type': config.config_type,
          'diff': sorted(diff.items())
          },
        context_instance=RequestContext(request))
