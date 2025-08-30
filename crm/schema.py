import re
import graphene

from graphene_django.filter import DjangoFilterConnectionField
from django.db import transaction
from graphene_django.types import DjangoObjectType
from .models import Customer, Product, Order

# GraphQL Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    class Meta:
        model = Order

class UpdateLowStockProducts(graphene.Mutation):
    updated_products = graphene.List(ProductType)
    message = graphene.String()

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated = []

        for product in low_stock_products:
            product.stock += 10
            product.save()
            updated.append(product)

        return UpdateLowStockProducts(
            updated_products=updated,
            message=f"{len(updated)} products restocked successfully."
        )

class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()

# Helper for phone validation
def validate_phone(phone):
    if not re.match(r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$', phone):
        raise ValueError("Invalid phone format. Use +1234567890 or 123-456-7890.")

class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        # Email uniqueness
        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists")

        # Phone format validation
        if phone:
            validate_phone(phone)

        customer = Customer.objects.create(name=name, email=email, phone=phone)
        return CreateCustomer(customer=customer, message="Customer created successfully")

class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter, order_by=graphene.List(of_type=graphene.String))
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter, order_by=graphene.List(of_type=graphene.String))
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter, order_by=graphene.List(of_type=graphene.String))

    def resolve_all_customers(self, info, **kwargs):
        qs = Customer.objects.all()
        order_by = kwargs.pop('order_by', None)
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def resolve_all_products(self, info, **kwargs):
        qs = Product.objects.all()
        order_by = kwargs.pop('order_by', None)
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

def resolve_all_orders(self, info, **kwargs):
        qs = Order.objects.all()
        order_by = kwargs.pop('order_by', None)
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()


