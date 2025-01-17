from django import template
from courierapp.models import CourierStatus

register = template.Library()

@register.filter
def get_current_step(flow_steps, shipment_status):
    # Convert flow_steps to a list if it's a dictionary
    steps = list(flow_steps.items())
    for step, label in steps:
        if step == shipment_status:
            return steps.index((step, label))  # Return the index of the current step
    return 0  # Default step if not found
