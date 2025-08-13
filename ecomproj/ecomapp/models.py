from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone


class UserProfileManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("You need to have an email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("SuperUser Must have Is_staff set to True")
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("SuperUser Must have Is_suoeruser set to True")
        return self.create_user(self, email, password=None, **extra_fields)
        
class UserProfile(AbstractUser):
    email = models.EmailField(max_length= 255,unique = True)

    objects = UserProfileManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    
    
class Category(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='categories', null=True)
    description = models.TextField(null= True , blank=True)
    image = models.ImageField(upload_to='products/',null= True , blank=True)
    sale_start = models.DateTimeField(null= True , blank=True)
    sale_end = models.DateTimeField(null= True , blank=True)
    is_active = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(null= True , blank=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0, null= True , blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #is_on_sale = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    def is_on_sale(self):
        now = timezone.now()
        # return now >= self.sale_start and now <= self.sale_end
        if self.sale_start and self.sale_end:
            return self.sale_start <= now <= self.sale_end
        return False

    
    def current_price(self):
        if self.is_on_sale:
            return float(self.price) * float((1 - self.discount / 100))
        else:
            return self.price
    
class Order(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE ,related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE , related_name='products')
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return f"Order {self.id} for {self.user.username}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderitems')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orderproducts')
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order Item {self.id} for {self.order.user.username}"

class Shoppingcart(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='shoppings')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='shopitems')
    quantity = models.PositiveIntegerField()
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Shopping Cart Item {self.id} for {self.username}"
    
class ShoppingCartItem(models.Model):
    shoppingcart = models.ForeignKey(Shoppingcart, on_delete=models.CASCADE, related_name='cart')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name= 'cartitems')
    quantity = models.PositiveIntegerField()
    added_at = models.DateTimeField(auto_now_add=True)
    