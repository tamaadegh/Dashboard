from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions  import AllowAny
from rest_framework.exceptions import APIException

from rest_framework import filters as drf_filters
import django_filters
from django_filters import rest_framework as filters
from django.contrib.postgres.search import TrigramSimilarity


from nxtbn.core.paginator import NxtbnPagination
from nxtbn.product.api.storefront.serializers import CategorySerializer, CollectionSerializer, ProductDetailImageListSerializer, ProductDetailSerializer, ProductDetailWithRelatedLinkImageListMinimalSerializer, ProductWithDefaultVariantImageListSerializer, ProductWithDefaultVariantSerializer, ProductWithVariantSerializer, ProductDetailWithRelatedLinkMinimalSerializer
from nxtbn.product.models import Category, Collection, Product
from nxtbn.product.models import Supplier
from nxtbn.core.currency.backend import currency_Backend


class ProductFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    summary = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
    category = filters.ModelChoiceFilter(field_name='category', queryset=Category.objects.all())
    category_name = filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    supplier = filters.ModelChoiceFilter(field_name='supplier', queryset=Supplier.objects.all())
    brand = filters.CharFilter(lookup_expr='icontains')
    type = filters.CharFilter(field_name='type', lookup_expr='exact')
    related_to = filters.CharFilter(field_name='related_to__name', lookup_expr='icontains')
    collection = filters.ModelChoiceFilter(field_name='collections', queryset=Collection.objects.all())

    class Meta:
        model = Product
        fields = ('name', 'summary', 'description', 'category', 'category_name', 'supplier', 'brand', 'type', 'related_to', 'collection')


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = NxtbnPagination
    permission_classes = (AllowAny,)
    queryset = Product.objects.all().select_related(
        'default_variant',
        'default_variant__image',
        'category',
        'supplier',
        'product_type',
        'tax_class'
    ).prefetch_related(
        'images',
        'variants',
        'translations',
        # 'translations' on ProductVariant might be needed if variants have their own translations
        'default_variant__translations',
        'related_to', 
    )
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        drf_filters.SearchFilter,
        drf_filters.OrderingFilter,
    ]
    filterset_class = ProductFilter
    search_fields = ['name', 'summary', 'description', 'category__name', 'brand']
    ordering_fields = ['name', 'created_at']
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = self.queryset
        # Defer heavy fields for list views to save memory and I/O
        if self.action in ['list', 'withvariant', 'with_recommended', 'with_recommended_image_list']:
            queryset = queryset.defer('description', 'metadata', 'internal_metadata')
        return queryset

    @method_decorator(cache_page(60 * 15)) # Cache for 15 minutes
    def list(self, request, *args, **kwargs):
        # We need to manually cache based on currency, as standard cache_page doesn't know about it
        return super().list(request, *args, **kwargs)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['exchange_rate'] = self.get_exchange_rate()
        return context

    def get_exchange_rate(self):
        if settings.IS_MULTI_CURRENCY:
            return currency_Backend().get_exchange_rate(self.request.currency)
        return 1.0


    def paginate_and_serialize(self, queryset): # NXTBN specific
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return  ProductWithDefaultVariantSerializer
        
        if self.action == 'retrieve': # Single product
            return ProductDetailSerializer
        
        if self.action == 'retrive_with_image_list': # single product
            return ProductDetailImageListSerializer
        
        if self.action == 'with_related': # Single product
            return ProductDetailWithRelatedLinkMinimalSerializer
        
        if self.action == 'with_related_image_list': # Single product
            return ProductDetailWithRelatedLinkImageListMinimalSerializer
        
        if self.action == 'with_recommended': # Single product
            return ProductWithDefaultVariantSerializer
        
        if self.action == 'with_recommended_image_list': # list via single product
            return ProductWithDefaultVariantImageListSerializer
        
        return ProductWithVariantSerializer
        

    @method_decorator(cache_page(60 * 15)) # Cache for 15 minutes
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='withvariant') # list
    def withvariant(self, request):
        queryset = self.filter_queryset(self.queryset)
        return self.paginate_and_serialize(queryset)
    
    @action(detail=True, methods=['get'])
    @method_decorator(cache_page(60 * 15))
    def with_related(self, request, slug=None):
        product = self.get_object()
        serializer = self.get_serializer(product)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    @method_decorator(cache_page(60 * 15))
    def with_related_image_list(self, request, slug=None):
        product = self.get_object()
        serializer = self.get_serializer(product)
        return Response(serializer.data)
    
    def _get_recommended_products(self, product):
        """
        Helper to fetch recommended products efficiently.
        1. Get IDs via TrigramSimilarity (lightweight query).
        2. Fetch full objects via configured queryset (heavyweight with prefetch).
        3. Preserve similarity order in Python.
        """
        # 1. Get IDs only
        similar_ids = list(Product.objects.annotate(
            similarity=TrigramSimilarity('name', product.name)
        ).order_by('-similarity').values_list('id', flat=True)[:20])

        if not similar_ids:
            return []

        # 2. Fetch full objects using the optimized queryset (with select_related/prefetch_related)
        # This prevents N+1 queries when accessing related fields in serializers
        recommended_products = list(self.get_queryset().filter(id__in=similar_ids))

        # 3. Sort in Python to match the Trigram order
        # Create a map for O(1) lookup
        product_map = {p.id: p for p in recommended_products}
        ordered_products = [product_map[pid] for pid in similar_ids if pid in product_map]
        
        return ordered_products

    @action(detail=True, methods=['get'])
    @method_decorator(cache_page(60 * 15))
    def with_recommended(self, request, slug=None):
        product = self.get_object()
        ordered_products = self._get_recommended_products(product)
        serializer = self.get_serializer(ordered_products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    @method_decorator(cache_page(60 * 15))
    def retrive_with_image_list(self, request, slug=None):
        product = self.get_object()
        serializer = self.get_serializer(product)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    @method_decorator(cache_page(60 * 15))
    def with_recommended_image_list(self, request, slug=None):
        product = self.get_object()
        ordered_products = self._get_recommended_products(product)
        serializer = self.get_serializer(ordered_products, many=True)
        return Response(serializer.data)
    
class CollectionListView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    pagination_class = None
    queryset = Collection.objects.filter(is_active=True).select_related('image')
    serializer_class = CollectionSerializer

    @method_decorator(cache_page(60 * 60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class CategoryListView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    pagination_class = None
    # Optimize recursive fetching: prefetch children up to depth 2 (as enforced by model)
    queryset = Category.objects.all().prefetch_related(
        'subcategories',
        'subcategories__subcategories'
    )
    serializer_class = CategorySerializer

    @method_decorator(cache_page(60 * 60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

