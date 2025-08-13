from django.shortcuts import render
from rest_framework.generics import (
    ListAPIView,  
    CreateAPIView, 
    RetrieveUpdateDestroyAPIView,
    )
from .serializers import ProductSerializer, AuthTokenSerializer, UserSerializer
from .models import Product, UserProfile
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.exceptions import ValidationError
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings



class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user
    
class UserListView(ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializer

class ProductPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100

class ProductList(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
    search_fields = ('name', 'description') 
    filterset_fields = ('id',) 
    pagination_class = ProductPagination
    ordering_fields = ('price') 

    def get_queryset(self):
        on_sale = str(self.request.query_params.get('is_on_sale', None))

        for parame,item in self.request.query_params.items():
            print(parame , item)

        if on_sale is None:
            return super().get_queryset()
        
        queryset = Product.objects.all()

        if on_sale == True:
            from django.utils import timezone
            now = timezone.now()
            return queryset.filter(sale_start__lte = now, sale_end__gte = now)
        return queryset
    
class ProductCreate(CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def create(self, request, *args, **kwargs):
        try:
            price = request.data.get('price')
            if price is not None and float(price) <= 0 :
                raise ValidationError({'price': ' must be above zero Rwf'})
        except ValueError:
            raise ValidationError({'price': ' a valid number must be provided'})
        
        return super().create(request, *args, **kwargs)


class ProductRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    lookup_field = 'id'
    serializer_class = ProductSerializer

    def delete(self, request, *args, **kwargs):
        product_id = request.data.get('id')
        response = super().delete(request, *args, **kwargs)
        if response.status_code == 204:
            from django.core.cache import cache
            cache.delete(f'product-{product_id}')
        return response
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        if response.status_code == 200:
            from django.core.cache import cache
            product = response.data
            cache.set(f'product-{product['id']}',{
                'name':product['name'],
                'description':product['description'],
                'price':product['price']
            })
        return response