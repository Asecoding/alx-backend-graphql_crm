import graphene
from django.db import transaction
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from .models import Customer, Product, Order
from .types import CustomerType, ProductType, OrderType


# ---------------- CreateCustomer ----------------
class CreateCustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)


class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CreateCustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, input):
        try:
            if Customer.objects.filter(email=input.email).exists():
                raise ValidationError("Email already exists.")

            customer = Customer(
                name=input.name,
                email=input.email,
                phone=input.phone if input.phone else ""
            )
            customer.full_clean()  # runs validators
            customer.save()
            return CreateCustomer(customer=customer, message="Customer created successfully.")
        except ValidationError as e:
            return CreateCustomer(customer=None, message=str(e))


# ---------------- BulkCreateCustomers ----------------
class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CreateCustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, input):
        created_customers = []
        errors = []

        with transaction.atomic():
            for idx, cust_data in enumerate(input, start=1):
                try:
                    if Customer.objects.filter(email=cust_data.email).exists():
                        raise ValidationError(f"Email {cust_data.email} already exists.")

                    customer = Customer(
                        name=cust_data.name,
                        email=cust_data.email,
                        phone=cust_data.phone if cust_data.phone else ""
                    )
                    customer.full_clean()
                    customer.save()
                    created_customers.append(customer)
                except ValidationError as e:
                    errors.append(f"Row {idx}: {str(e)}")

        return BulkCreateCustomers(customers=created_customers, errors=errors)


# ---------------- CreateProduct ----------------
class CreateProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(required=False, default_value=0)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = CreateProductInput(required=True)

    product = graphene.Field(ProductType)

    @classmethod
    def mutate(cls, root, info, input):
        if input.price <= 0:
            raise ValidationError("Price must be positive.")
        if input.stock < 0:
            raise ValidationError("Stock cannot be negative.")

        product = Product.objects.create(
            name=input.name,
            price=input.price,
            stock=input.stock
        )
        return CreateProduct(product=product)


# ---------------- CreateOrder ----------------
class CreateOrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime(required=False)


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = CreateOrderInput(required=True)

    order = graphene.Field(OrderType)
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, input):
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except ObjectDoesNotExist:
            return CreateOrder(order=None, message="Invalid customer ID.")

        products = Product.objects.filter(pk__in=input.product_ids)
        if not products.exists():
            return CreateOrder(order=None, message="Invalid product IDs provided.")

        if len(products) != len(input.product_ids):
            return CreateOrder(order=None, message="Some product IDs are invalid.")

        if not products:
            return CreateOrder(order=None, message="At least one product is required.")

        order = Order.objects.create(customer=customer, order_date=input.order_date or None)
        order.products.set(products)
        order.calculate_total()

        return CreateOrder(order=order, message="Order created successfully.")
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
