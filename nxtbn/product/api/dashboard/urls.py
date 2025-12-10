from django.urls import path, include, register_converter
from rest_framework.routers import DefaultRouter

from nxtbn.core.url_converters import IdOrNoneConverter

from nxtbn.product.api.dashboard.views import (
    ProductListView,
    ProductDetailView,
    CategoryListView,
    CategoryByParentView,
    CategoryDetailView,
    CollectionViewSet,
    RecursiveCategoryListView,
    ColorViewSet,
    ProductTypeViewSet,
    ProductTagViewSet,
    ProductVariantDeleteAPIView,
    ProductWithVariantView,
    ProductMinimalListView,
    ProductListDetailVariantView,
    TaxClassView,
    BulkProductStatusUpdateAPIView,
    BulkProductDeleteAPIView,
    ProductVariants,
    InventoryListView,
    SupplierModelViewSet
)

register_converter(IdOrNoneConverter, 'id_or_none')


router = DefaultRouter()
router.register(r'colors', ColorViewSet)
router.register(r'product-types', ProductTypeViewSet)
router.register(r'product-tags', ProductTagViewSet)
router.register(r'collections', CollectionViewSet)
router.register(r'suppliers', SupplierModelViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/minimal/', ProductMinimalListView.as_view(), name='product-minimal-list'),
    path('products/with-detailed-variants/', ProductListDetailVariantView.as_view(), name='product-list-with-detailed-variants'),
    path('products/<int:id>/', ProductDetailView.as_view(), name='product-detail'),
    path('product-with-variants/<int:id>/', ProductWithVariantView.as_view(), name='product-with-variant'),
    path('variants/<int:pk>/', ProductVariantDeleteAPIView.as_view(), name='variant-delete'),

    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('recursive-categories/', RecursiveCategoryListView.as_view(), name='recursive-category'),
    path('categories/<int:id>/', CategoryDetailView.as_view(), name='category-detail'),
    path('categories-by-parent/<id_or_none:id>/', CategoryByParentView.as_view(), name='category-by-parent'),
    path('tax-class/', TaxClassView.as_view(), name='tax-class'),
    path('products/update/bulk/', BulkProductStatusUpdateAPIView.as_view(), name='bulk-product-status-update'),
    path('products/delete/bulk/', BulkProductDeleteAPIView.as_view(), name='bulk-product-status-delete'),
    path('products-variants/', ProductVariants.as_view(), name='products-variants'),
    path('inventory/', InventoryListView.as_view(), name='product-inventory'),

]

