from django import template

register = template.Library()


@register.inclusion_tag('manager_core/paginator.html', takes_context=True)
def pagination(context):
    """Get page range to omit pages far away from current page."""
    show_first = False
    show_last = False

    pages_count = context['paginator'].num_pages
    page_number = context['page_obj'].number

    # Minimum pages: 5 pages(current page +- 2 pages)
    if pages_count <= 5:
        return {
            'show_first': show_first,
            'page_range': range(1, pages_count+1),
            'show_last': show_last,
            'page_obj': context['page_obj'],
            'paginator': context['paginator']
        }

    page_range = [x for x in range(page_number - 2, page_number + 3) if 1 <= x <= pages_count]

    if 1 not in page_range:
        show_first = True

    if pages_count not in page_range:
        show_last = True

    return {
        'show_first': show_first,
        'page_range': page_range,
        'show_last': show_last,
        'page_obj': context['page_obj'],
        'paginator': context['paginator']
    }

