from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User


# Create your models here.
class User(AbstractUser):
    username=models.CharField(max_length=50,blank=True,null=True)
    email=models.EmailField(unique=True)
    
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username']
    

class Product(models.Model):
    name=models.CharField(max_length=50)
    price=models.DecimalField(max_digits=6,decimal_places=2)
    brand=models.CharField(max_length=15)
    model=models.CharField(max_length=15)
    rating=models.DecimalField(max_digits=2,decimal_places=1,default=0.0)
    image=models.ImageField(upload_to='product/',null=True,blank=True)
    
class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveBigIntegerField(default=1)
    
class Order(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)
    address=models.TextField(default="Nor provide")
    payment_methd=models.CharField(max_length=50,default=50)
    order_at=models.DateTimeField(auto_now_add=True)
    
    def total_price(self):
        return self.product.price*self.quantity