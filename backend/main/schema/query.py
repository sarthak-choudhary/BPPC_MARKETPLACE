import graphene
from django.core.exceptions import ObjectDoesNotExist
from graphql_jwt.decorators import login_required

from main import models
from main.schema import utils
from main.schema.types import (Category, Product, ProductOffer,
                               PaginatedProducts, Profile, UserReport, PaginatedProfiles)

from main.documents import ProductDocument


class Query:
    all_categories = graphene.List(Category)
    all_profiles = graphene.List(Profile)
    category = graphene.Field(Category, name=graphene.String())
    product = graphene.Field(Product, id=graphene.Int())
    profile = graphene.Field(Profile, id=graphene.Int(), username=graphene.String(), email=graphene.String())
    my_profile = graphene.Field(Profile)
    product_offer = graphene.List(ProductOffer, id=graphene.Int())
    wishlist = graphene.Field(PaginatedProducts, page=graphene.Int(), pagesize=graphene.Int())
    products = graphene.Field(PaginatedProducts, page=graphene.Int(), pagesize=graphene.Int())
    profiles = graphene.Field(PaginatedProfiles, page=graphene.Int(), pagesize=graphene.Int())

    search_products = graphene.Field(PaginatedProducts, page=graphene.Int(), pagesize=graphene.Int(), querystring=graphene.String())

    @login_required
    def resolve_all_categories(self, info, **kwargs):
        return models.Category.objects.all()

    @login_required
    def resolve_all_profiles(self, info, **kwargs):
        return models.Profile.objects.all()

    @login_required
    def resolve_category(self, info, **kwargs):
        name = kwargs.get('name')

        if name is not None:
            return models.Category.objects.get(name=name)
        return None

    @login_required
    def resolve_product(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            try:
                return models.Product.objects.get(id=id)
            except ObjectDoesNotExist:
                return None
        return None

    @login_required
    def resolve_profile(self, info, id=None, username=None, email=None):
        if username is not None:
            try:
                user = models.User.objects.get(username=username)
            except ObjectDoesNotExist:
                return None
            return user.profile

        if id is not None:
            try:
                return models.Profile.objects.get(id=id)
            except ObjectDoesNotExist:
                return None
        if email is not None:
            try:
                return models.Profile.objects.get(email=email)
            except ObjectDoesNotExist:
                return None
        return None

    # profile.wishlist.products.all()
    @login_required
    def resolve_wishlist(self, info, page, pagesize):
        profile = info.context.user.profile

        if profile is None:
            return None
        
        page_size = pagesize
        qs = profile.wishlist.products.all()
        return utils.get_paginator(qs, page_size, page, PaginatedProducts)
        
    @login_required
    def resolve_product_offer(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            try:
                product = models.Product.objects.get(id=id)
            except ObjectDoesNotExist:
                return None
            return product.offers.all()

        return None

    @login_required
    def resolve_products(self, info, page, pagesize):
        page_size = pagesize
        qs = models.Product.objects.all().order_by("created_at")
        return utils.get_paginator(qs, page_size, page, PaginatedProducts)

    @login_required
    def resolve_my_profile(self, info, **kwargs):
        profile = info.context.user.profile
        return profile

    @login_required
    def resolve_search_products(self, info, page, pagesize, **kwargs):
        querystring = kwargs.get('querystring')
        hits = ProductDocument.search().query("multi_match", fields=['name', 'description'],  query=querystring)
        print(hits)
        qs = hits.to_queryset()
        page_size = pagesize
        return utils.get_paginator(qs, page_size, page, PaginatedProducts)

    @login_required
    def resolve_profiles(self, info, page, pagesize):
        page_size = pagesize
        qs = models.Profile.objects.all()
        return utils.get_paginator(qs, page_size, page, PaginatedProfiles)

