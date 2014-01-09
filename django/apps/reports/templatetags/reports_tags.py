from django.template import Library

from ..forms import ReportResolveForm

register = Library()


@register.inclusion_tag('forms/simple.html', takes_context=True)
def resolve_form(context, report):
    """Displays a resolve form."""
    if not report.is_erased:
        path = context['request'].get_full_path()
        form = ReportResolveForm(report=report, next=path)
        return {'form': form}
    else:
        return {'form': None}
