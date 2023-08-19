from rest_framework.serializers import ModelSerializer, ListField, ValidationError

from .models import Order, OrderedProduct


class ProductObjectSerializer(ModelSerializer):
    class Meta:
        model = OrderedProduct
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = ListField(write_only=True, child=ProductObjectSerializer(), allow_empty=False)

    def create(self, validated_data):
        products = validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        for product in products:
            new_product_object = OrderedProduct.objects.create(
                product=product['product'],
                quantity=product['quantity'],
                order=order,
                fixed_price=product['product'].price
            )
        return order

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'phonenumber', 'address', 'products']
