import django_filters as filters
from nxtbn.product.models import Category, Collection, Product, ProductTag, ProductVariant, Supplier
from django.db.models import Q


class ProductFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search', label='Search Across Multiple Fields')
    name = filters.CharFilter(lookup_expr='icontains')
    summary = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
    category = filters.ModelChoiceFilter(field_name='category', queryset=Category.objects.all())
    category_name = filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    supplier = filters.ModelChoiceFilter(field_name='supplier', queryset=Supplier.objects.all())
    brand = filters.CharFilter(lookup_expr='icontains')
    related_to = filters.CharFilter(field_name='related_to__name', lookup_expr='icontains')
    collection = filters.ModelChoiceFilter(field_name='collections', queryset=Collection.objects.all())

    class Meta:
        model = Product
        fields = ('name', 'summary', 'description', 'category', 'category_name', 'supplier', 'brand','related_to', 'search', 'collection')

    def filter_search(self, queryset, name, value):
        """
        Custom search method to search across multiple fields: name, description, and alias.
        """
        lookup = Q(name__icontains=value) | Q(description__icontains=value) | Q(alias__icontains=value)
        return queryset.filter(lookup)
    


class CategoryFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Category
        fields = ('name',)


class CollectionFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Collection
        fields = ('name',)


class ProductTagsFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = ProductTag
        fields = ('name',)


class SupplierFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Supplier
        fields = ('name',)

class ProductVariantFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = ProductVariant
        fields = ('name',)