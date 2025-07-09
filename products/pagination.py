from rest_framework.pagination import BasePagination
from rest_framework.response import Response

class SearchAfterRelevancePagination(BasePagination):
    """
    Pages through Elasticsearch Search results ordered by relevance (_score) and id as tie-breaker.
    Reads `page_size` and `search_after` from query params.
    """
    default_page_size = 20
    max_page_size = 100
    page_size_query_param = 'page_size'
    search_after_param = 'search_after'

    def paginate_queryset(self, search, request, view=None):
        """
        `search` is an instance of elasticsearch_dsl.Search
        """
        self.request = request

        # Read page_size from query params, enforce limits
        try:
            self.page_size = min(
                int(request.query_params.get(self.page_size_query_param, self.default_page_size)),
                self.max_page_size
            )
        except (ValueError, TypeError):
            self.page_size = self.default_page_size

        # Apply sort: first by _score desc, then by id asc for stable ordering
        search = search.sort(
            {'_score': {'order': 'desc'}},
            {'id': {'order': 'asc'}}
        )

        # Parse search_after if provided
        raw = request.query_params.get(self.search_after_param)
        if raw:
            # Expect raw like "<score>,<id>"
            score_str, id_str = raw.split(',')
            try:
                score = float(score_str)
            except ValueError:
                score = None
            if score is not None:
                search = search.extra(search_after=[score, id_str])

        # Retrieve one extra record to detect next page
        response = search[0:self.page_size + 1].execute()
        hits = response.hits

        # Store hits for building next pointer
        self.hits = hits
        # Return only the requested page size
        return hits[:self.page_size]

    def get_paginated_response(self, data):
        next_search_after = None
        # If more hits than page_size, we have a next page
        if len(self.hits) > self.page_size:
            last = self.hits[self.page_size - 1]
            next_search_after = f"{last.meta.score},{last.id}"

        return Response({
            'next_search_after': next_search_after,
            'results': data
        })
