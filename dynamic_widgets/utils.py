from django.db.models import Q

def django_admin_keyword_search(queryset, keywords, search_fields):
    '''Search according to fields defined in Admin's search_fields'''
    all_queries = None

    for keyword in keywords.split(' '):
        keyword_query = None

        for field in search_fields:
            each_query = Q(**{field+'__icontains':keyword})

            if not keyword_query:
                keyword_query = each_query
            else:
                keyword_query = keyword_query | each_query

        if not all_queries:
            all_queries = keyword_query
        else:
            all_queries = all_queries & keyword_query

    result_set = queryset.filter(all_queries).distinct()

    return result_set