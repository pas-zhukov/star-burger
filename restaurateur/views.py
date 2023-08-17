import requests
from geopy import distance
from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.db.models import Q
from django.conf import settings

from foodcartapp.models import Product, Restaurant, Order
from locations.models import Place

class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    unfinished_orders = Order.objects.filter(~Q(status=3)).with_prices().prefetch_related('products__product')
    for order in unfinished_orders:
        restaurants = Restaurant.objects.all().prefetch_related('menu_items')
        order_restaurants = get_available_restaurants(order, restaurants)
        try:
            order_coords = fetch_coordinates(order.address, settings.YANDEX_GEOCODER_KEY)
            for restaurant in order_restaurants:
                restaurant_coords = fetch_coordinates(restaurant.address, settings.YANDEX_GEOCODER_KEY)
                restaurant.order_distance = round(distance.distance(restaurant_coords, order_coords).km, 2)
            order.restaurants = sorted(order_restaurants, key=lambda r: r.order_distance)
        except GEOCoderError:
            order.restaurants = 'ERROR'

    return render(request, template_name='order_items.html', context={
        'order_items': unfinished_orders,
        'redirect_url': request.path,
    })


def get_available_restaurants(order, restaurants):
    available_restaurants = []
    products = [product.product for product in order.products.all()]
    for restaurant in restaurants:
        menu_items = restaurant.menu_items.filter(availability=True).select_related('product')
        menu_products = [item.product for item in menu_items]
        if set(products).issubset(menu_products):
            available_restaurants.append(restaurant)
    return available_restaurants


def fetch_coordinates(address, apikey):
    try:
        place = Place.objects.get(address=address)
    except Place.DoesNotExist:
        base_url = "https://geocode-maps.yandex.ru/1.x"
        response = requests.get(base_url, params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        })
        response.raise_for_status()
        found_places = response.json()['response']['GeoObjectCollection']['featureMember']

        if not found_places:
            raise GEOCoderError

        most_relevant = found_places[0]
        lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
        place = Place.objects.create(address=address,
                                     lon=lon,
                                     lat=lat)
    return place.lon, place.lat


class GEOCoderError(Exception):
    def __init__(self, message: str = 'Error while locating specified address.'):
        super().__init__(message)
