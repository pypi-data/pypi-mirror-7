"""
Custom template tags for displaying tour navigation
"""
from copy import deepcopy
import json

from django import template
from django.template.loader import get_template

from tour.api import TourResource
from tour.models import Tour


register = template.Library()


class TourNavNode(template.Node):
    def __init__(self, always_show=False):
        self.always_show = always_show

    def get_tour_class(self, request):
        # Check for any tours
        tour_class = Tour.objects.get_for_user(request.user)
        if not tour_class and self.always_show:
            tour_class = Tour.objects.get_recent_tour(request.user)
        if self.always_show:
            mutable_get = deepcopy(request.GET)
            mutable_get['always_show'] = True
            request.GET = mutable_get
        return tour_class

    def get_tour_dict(self, tour_class, request):
        if tour_class:
            # Serialize the tour and its steps
            tour = tour_class.tour
            tour_resource = TourResource()
            tour_bundle = tour_resource.build_bundle(obj=tour, request=request)
            tour_data = tour_resource.full_dehydrate(tour_bundle)
            tour_json = tour_resource.serialize(None, tour_data, 'application/json')
            tour_dict = json.loads(tour_json)

            # Set the step css classes
            previous_steps_complete = True
            is_after_current = False
            tour_dict['display_name'] = tour.name
            for step_dict in tour_dict['steps']:
                cls = ''
                if step_dict['url'] == request.path:
                    cls += 'current '
                    step_dict['current'] = True
                    tour_dict['display_name'] = step_dict['name']
                    is_after_current = True
                if not previous_steps_complete:
                    cls += 'incomplete unavailable '
                    step_dict['url'] = '#'
                elif not step_dict['complete']:
                    cls += 'incomplete available '
                    previous_steps_complete = False
                elif is_after_current:
                    cls += 'available '
                else:
                    cls += 'complete available '
                step_dict['cls'] = cls

            return tour_dict
        return {}

    def render(self, context):
        if 'request' in context and hasattr(context['request'], 'user'):
            # Make sure this isn't the anonymous user
            if not context['request'].user.id:
                return ''

            tour_class = self.get_tour_class(context['request'])
            context['tour'] = self.get_tour_dict(tour_class, context['request'])

            # Load the tour template and render it
            tour_template = get_template('tour/tour_navigation.html')
            return tour_template.render(context)
        return ''


@register.simple_tag(takes_context=True)
def tour_navigation(context, **kwargs):
    """
    Tag to render the tour nav node
    """
    return TourNavNode(always_show=kwargs.get('always_show', False)).render(context)
