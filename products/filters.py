from django_elasticsearch_dsl_drf.filter_backends import BaseSearchFilterBackend
from elasticsearch_dsl.query import MultiMatch

class FuzzySearchFilterBackend(BaseSearchFilterBackend):
    def filter_queryset(self, request, queryset, view):
        query = request.query_params.get('search', None)
        if not query:
            return queryset
        
        queryset =  queryset.query(
            MultiMatch(
                query=query,
                fields=[
                    'title_fa_ngram^2',
                    'title_en',
                    'tags_fa_ngram',
                ],
                fuzziness='AUTO',
                prefix_length=1,
                type='best_fields',
            )
        )
        return queryset
