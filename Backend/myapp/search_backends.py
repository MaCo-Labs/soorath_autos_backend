# Backend/myapp/search_backends.py
from django.contrib.postgres.search import (
    SearchVector, SearchQuery, SearchRank, TrigramSimilarity, TrigramDistance
)
from django.db.models import Q, Value, FloatField
from django.db.models.functions import Greatest
from rest_framework import filters


SIMILARITY_THRESHOLD = 0.2   # 0.0–1.0; lower = more forgiving typos
MIN_RANK = 0.01              # minimum full-text rank to include a result


class FuzzySearchBackend(filters.BaseFilterBackend):
    """
    PostgreSQL-powered fuzzy search using pg_trgm + full-text search.

    - Handles typos:  'toyta' → Toyota
    - Case-insensitive automatically
    - Ranks results by relevance (best matches first)
    - Falls back gracefully if no query param
    """

    search_param = 'search'

    def filter_queryset(self, request, queryset, view):
        query = request.query_params.get(self.search_param, '').strip()
        if not query:
            return queryset

        # ── 1. Full-text search (exact word / prefix matches, highest rank) ──
        search_vector = SearchVector('brand', weight='A') + \
                        SearchVector('model', weight='A') + \
                        SearchVector('description', weight='B')
        search_query = SearchQuery(query, search_type='websearch')

        # ── 2. Trigram similarity (fuzzy / typo matching) ──
        brand_sim = TrigramSimilarity('brand', query)
        model_sim = TrigramSimilarity('model', query)
        best_sim  = Greatest(brand_sim, model_sim, output_field=FloatField())

        # ── 3. Combine: return rows that pass EITHER filter ──
        queryset = (
            queryset
            .annotate(
                search_rank=SearchRank(search_vector, search_query),
                similarity=best_sim,
            )
            .filter(
                Q(search_rank__gte=MIN_RANK) |       # full-text hit
                Q(similarity__gte=SIMILARITY_THRESHOLD)  # fuzzy/typo hit
            )
            .order_by('-search_rank', '-similarity', '-id')
        )

        return queryset

    def get_schema_operation_parameters(self, view):
        return [{
            'name': self.search_param,
            'required': False,
            'in': 'query',
            'description': 'Fuzzy search across brand, model, description',
            'schema': {'type': 'string'},
        }]