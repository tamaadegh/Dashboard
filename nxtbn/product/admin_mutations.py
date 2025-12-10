import graphene
from nxtbn.core.admin_permissions import gql_required_perm
from nxtbn.product.admin_types import CategoryTranslationType, CategoryType, CollectionTranslationType, ProductTagTranslationType, ProductTranslationType, ProductVariantTranslationType, SupplierTranslationType
from nxtbn.product.models import Category, CategoryTranslation, CollectionTranslation, ProductTagTranslation, ProductTranslation, ProductVariantTranslation, SupplierTranslation
from nxtbn.users import UserRole


class NameSecriptionSEOInputType(graphene.InputObjectType):
    name = graphene.String(required=True)
    description = graphene.String(required=True)
    meta_title = graphene.String(required=True)
    meta_description = graphene.String(required=True)


class UpdateCategoryMutation(graphene.Mutation):
    class Arguments:
        input = NameSecriptionSEOInputType(required=True)
        id = graphene.Int(required=True)
    
    category = graphene.Field(CategoryType)

    @gql_required_perm(Category, 'change_category')
    def mutate(self, info, id, input):
        category = Category.objects.get(id=id)
        category.name = input.name
        category.description = input.description
        category.meta_title = input.meta_title
        category.meta_description = input.meta_description
        category.save()

        return UpdateCategoryMutation(category=category)


# ================================
# All Transaltoin Mutations
# ================================

class UpdateProductTranslatoinMutation(graphene.Mutation):
    class Arguments:
        base_product_id = graphene.Int(required=True)
        lang_code = graphene.String(required=True)
        name = graphene.String()
        summary = graphene.String()
        description = graphene.String()
        meta_title = graphene.String()
        meta_description = graphene.String()

    product_translation = graphene.Field(ProductTranslationType)

    @gql_required_perm(ProductTranslation, 'change_producttranslation')
    def mutate(self, info, base_product_id, lang_code, name, summary, description, meta_title, meta_description):
        try:
            product_translation = ProductTranslation.objects.get(product_id=base_product_id, language_code=lang_code)
        except ProductTranslation.DoesNotExist:
            product_translation = ProductTranslation(product_id=base_product_id, language_code=lang_code)

        product_translation.name = name
        product_translation.summary = summary
        product_translation.description = description
        product_translation.meta_title = meta_title
        product_translation.meta_description = meta_description
        product_translation.save()

        return UpdateProductTranslatoinMutation(product_translation=product_translation) 
    

class UpdateCategoryTranslationMutation(graphene.Mutation):
    class Arguments:
        base_category_id = graphene.Int(required=True)
        lang_code = graphene.String(required=True)
        name = graphene.String()
        description = graphene.String()
        meta_title = graphene.String()
        meta_description = graphene.String()

    category_translation = graphene.Field(CategoryTranslationType)

    @gql_required_perm(CategoryTranslation, 'change_categorytranslation')
    def mutate(self, info, base_category_id, lang_code, name, description, meta_title, meta_description):
        try:
            category_translation = CategoryTranslation.objects.get(category_id=base_category_id, language_code=lang_code)
        except CategoryTranslation.DoesNotExist:
            category_translation = CategoryTranslation(category_id=base_category_id, language_code=lang_code)

        category_translation.name = name
        category_translation.description = description
        category_translation.meta_title = meta_title
        category_translation.meta_description = meta_description
        category_translation.save()

        return UpdateCategoryTranslationMutation(category_translation=category_translation)
    

class UpdateSupplierTranslationMutation(graphene.Mutation):
    class Arguments:
        base_supplier_id = graphene.Int(required=True)
        lang_code = graphene.String(required=True)
        name = graphene.String()
        description = graphene.String()
        meta_title = graphene.String()
        meta_description = graphene.String()

    supplier_translation = graphene.Field(SupplierTranslationType)

    @gql_required_perm(SupplierTranslation, 'change_suppliertranslation')
    def mutate(self, info, base_supplier_id, lang_code, name, description, meta_title, meta_description):
        try:
            supplier_translation = SupplierTranslation.objects.get(supplier_id=base_supplier_id, language_code=lang_code)
        except SupplierTranslation.DoesNotExist:
            supplier_translation = SupplierTranslation(supplier_id=base_supplier_id, language_code=lang_code)

        supplier_translation.name = name
        supplier_translation.description = description
        supplier_translation.meta_title = meta_title
        supplier_translation.meta_description = meta_description
        supplier_translation.save()

        return UpdateSupplierTranslationMutation(supplier_translation=supplier_translation)
    

class UpdateProductVariantTranslationMutation(graphene.Mutation):
    class Arguments:
        base_product_variant_id = graphene.Int(required=True)
        lang_code = graphene.String(required=True)
        name = graphene.String()

    product_variant_translation = graphene.Field(ProductVariantTranslationType)

    @gql_required_perm(ProductVariantTranslation, 'change_productvarianttranslation')
    def mutate(self, info, base_product_variant_id, lang_code, name, description, meta_title, meta_description):
        try:
            product_variant_translation = ProductVariantTranslation.objects.get(product_variant_id=base_product_variant_id, language_code=lang_code)
        except ProductVariantTranslation.DoesNotExist:
            product_variant_translation = ProductVariantTranslation(product_variant_id=base_product_variant_id, language_code=lang_code)

        product_variant_translation.name = name
        product_variant_translation.save()

        return UpdateProductVariantTranslationMutation(product_variant_translation=product_variant_translation)
    
class UpdateProductTagsTranslationMutation(graphene.Mutation):
    class Arguments:
        base_product_tag_id = graphene.Int(required=True)
        lang_code = graphene.String(required=True)
        name = graphene.String()

    product_tag_translation = graphene.Field(ProductTagTranslationType)

    @gql_required_perm(ProductTagTranslation, 'change_producttagtranslation')
    def mutate(self, info, base_product_tag_id, lang_code, name, description, meta_title, meta_description):
        try:
            product_tag_translation = ProductTagTranslation.objects.get(product_tag_id=base_product_tag_id, language_code=lang_code)
        except ProductTagTranslation.DoesNotExist:
            product_tag_translation = ProductTagTranslation(product_tag_id=base_product_tag_id, language_code=lang_code)

        product_tag_translation.name = name
        product_tag_translation.save()

        return UpdateProductTagsTranslationMutation(product_tag_translation=product_tag_translation)

class UpdateProductCollectionTranslationMutation(graphene.Mutation):
    class Arguments:
        base_collection_id = graphene.Int(required=True)
        lang_code = graphene.String(required=True)
        name = graphene.String()
        description = graphene.String()
        meta_title = graphene.String()
        meta_description = graphene.String()

    collection_translation = graphene.Field(CollectionTranslationType)

    @gql_required_perm(CollectionTranslation, 'change_collectiontranslation')
    def mutate(self, info, base_collection_id, lang_code, name, description, meta_title, meta_description):
        try:
            collection_translation = CollectionTranslation.objects.get(collection_id=base_collection_id, language_code=lang_code)
        except CollectionTranslation.DoesNotExist:
            collection_translation = CollectionTranslation(collection_id=base_collection_id, language_code=lang_code)

        collection_translation.name = name
        collection_translation.description = description
        collection_translation.meta_title = meta_title
        collection_translation.meta_description = meta_description
        collection_translation.save()

        return UpdateProductCollectionTranslationMutation(collection_translation=collection_translation)


class ProductMutation(graphene.ObjectType):
    update_category = UpdateCategoryMutation.Field()

    # All Transaltion Mutations
    update_product_translation = UpdateProductTranslatoinMutation.Field()
    update_category_translation = UpdateCategoryTranslationMutation.Field()
    update_supplier_translation = UpdateSupplierTranslationMutation.Field()
    update_product_variant_translation = UpdateProductVariantTranslationMutation.Field()
    update_product_tag_translation = UpdateProductTagsTranslationMutation.Field()
    update_collection_translation = UpdateProductCollectionTranslationMutation.Field()

