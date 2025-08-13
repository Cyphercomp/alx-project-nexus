from django.urls import path
from .views import *

urlpatterns = [
    path('api-auth/v1/user/create', CreateUserView.as_view()),
    path('api-auth/v1/user/', UserListView.as_view()),
    path('api/v1/products', ProductList.as_view()),
    path('api/v1/products/new', ProductCreate.as_view()),
    path('api/v1/products/<int:id>', ProductRetrieveUpdateDestroyView.as_view()),
    # path('api/v1/products/<int:pk>/update', ProductUpdate.as_view()),
    # path('api/v1/products/<int:id>/delete', ProductDelete.as_view()),
    
  
]