import re
import graphene
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

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
