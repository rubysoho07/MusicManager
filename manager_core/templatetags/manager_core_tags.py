from django import template
from django.db.models import Q

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


@register.inclusion_tag('manager_core/album_item.html', takes_context=True)
def album_info(context, album_link, add_delete_button):
    """Get basic information for an album."""

    information = dict()

    information['album'] = context['album'] if 'album' in context else context['object']
    information['album_link'] = album_link
    information['artist_link'] = True
    information['show_additional_info'] = True
    information['user'] = context['user']

    # Make add/delete button.
    if add_delete_button is True and information['user'].is_authenticated():
        my_album = information['album'].mmuseralbum_set.filter(Q(user=information['user']))
        if len(my_album) == 0:
            information['add_user_album'] = True
        else:
            information['delete_user_album'] = True
            information['user_album_id'] = my_album[0].id

    return information


@register.inclusion_tag('manager_core/album_item.html', takes_context=True)
def album_info_external(context):
    """Get basic information for an album from parsed data."""
    information = dict()

    information['album'] = context['album']
    information['external_cover'] = context['external_cover']

    return information


@register.inclusion_tag('manager_core/album_item.html', takes_context=True)
def user_album_info(context):
    """Get basic information for an album."""

    information = dict()

    information['album'] = context['user_album'].album
    information['album_link'] = True
    information['artist_link'] = True
    information['show_additional_info'] = True
    information['user'] = context['user']

    # Make add/delete button.
    if information['user'].is_authenticated():
        my_album = information['album'].mmuseralbum_set.filter(Q(user=information['user']))
        if len(my_album) == 0:
            information['add_user_album'] = True
        else:
            information['delete_user_album'] = True
            information['user_album_id'] = my_album[0].id

    # Make a form for rating an album.
    if information['user'] == context['view_owner']:
        information['rating_form'] = True
        information['my_score'] = context['user_album'].score
        information['score_iterator'] = range(1, 11)

    return information
