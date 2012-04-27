# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

import logging

from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext

from lizard_portal.models import ConfigurationToValidate

logger = logging.getLogger(__name__)

def view_config_diff(request, area_name, config_type,
                            template='lizard_validation/config_diff.html'):
    logger.debug('lizard_validation.views.view_config_diff')
    logger.debug('look for ConfigurationToValidate for Area with name: %s', area_name)
    config = get_object_or_404(ConfigurationToValidate,
        area__name=area_name, config_type=config_type)
    diff = {
        '3201 (Stichtsch Ankeveensche Polder)': {
            'DIEPTE': ('1.17', '1.18'),
            'EXTINCTIE': ('0.5', '0.55'),
            'MOERAS_OR': ('False', 'True'),
            }
        }
    return render_to_response(
        template,
        { 'name': config.area.name,
          'type': config.config_type,
          'diff': diff,
        },
        context_instance=RequestContext(request))
