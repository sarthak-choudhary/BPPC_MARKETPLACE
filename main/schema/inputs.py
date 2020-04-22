import graphene

class ProductInput(graphene.InputObjectType):
    id = graphene.ID()
    name = graphene.String()
    base_price = graphene.Int()
    description = graphene.String()
    sold = graphene.Boolean()
    category = graphene.Int()
    seller = graphene.ID()

