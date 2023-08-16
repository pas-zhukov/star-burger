import json

from django.http import JsonResponse
from django.templatetags.static import static
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.serializers import ModelSerializer, ListField, ValidationError, IntegerField
from phonenumber_field.phonenumber import PhoneNumber

from .models import Product, Order, ProductObject


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


class ProductObjectSerializer(ModelSerializer):

    class Meta:
        model = ProductObject
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = ListField(write_only=True, child=ProductObjectSerializer(), allow_empty=False)

    def validate_phonenumber(self, value):
        phonenumber = PhoneNumber.from_string(value, 'RU')
        if not phonenumber.is_valid():
            raise ValidationError('Invalid phone number.')
        return value

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'phonenumber', 'address', 'products']


@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    order_params = serializer.validated_data
    order = Order.objects.create(
        address=order_params['address'],
        firstname=order_params['firstname'],
        lastname=order_params['lastname'],
        phonenumber=order_params['phonenumber']
    )
    for product in order_params['products']:
        new_product_object = ProductObject.objects.create(product=product['product'],
                                                          quantity=product['quantity'],
                                                          order=order)
    response = OrderSerializer(order).data
    return Response(response)
