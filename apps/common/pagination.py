from django.core.paginator import Paginator

from .constants import DEFAULT_PAGE, PAGINATION_PAGE_SIZE


def paginate_queryset(queryset, page_number=DEFAULT_PAGE, per_page=PAGINATION_PAGE_SIZE):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(page_number)
