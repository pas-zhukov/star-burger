import json

from django.http import JsonResponse
from django.templatetags.static import static
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

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


@api_view(['POST'])
def register_order(request):
    result, msg = check_register_order_data(request.data)
    if not result:
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)
    order_params = request.data
    order = Order.objects.create(
        customer_address=order_params['address'],
        customer_firstname=order_params['firstname'],
        customer_lastname=order_params['lastname'],
        customer_phonenumber=order_params['phonenumber']
    )
    for product in order_params['products']:
        new_product = get_object_or_404(Product, id=product['product'])
        new_product_object = ProductObject.objects.create(product=new_product,
                                                          count=product['quantity'],
                                                          order=order)
        new_product_object.save()
    order.save()
    return Response(order_params)


def check_register_order_data(data):
    if not isinstance(data, dict):
        return False, 'All the data should be contained in a dictionary.'

    required_fields = ['address', 'firstname', 'lastname', 'phonenumber', 'products']
    for field in required_fields:
        if not field in data:
            return False, f'{field.title()} field is missing.'

    if not isinstance(data['products'], list):
        return False, 'Products must be listed in s list.'

    if not data['products']:
        return False, "Products list can't be empty."

    for product in data['products']:
        if not isinstance(product['quantity'], int):
            return False, 'Product quantity must be defined as integer.'
        if product['quantity'] <= 0:
            return False, 'Product quantity must be greater than 0.'

    return True, 'Data is ok.'
