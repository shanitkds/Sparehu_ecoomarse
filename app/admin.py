from django.contrib import admin
from .models import User,Product,Cart,Order

class viewCart_info(admin.ModelAdmin):
    list_display=('product_id','product')

class Vieworder_info(admin.ModelAdmin):
    list_display=('id',)
# Register your models here.
admin.site.register(User)
admin.site.register(Product)
admin.site.register(Cart,viewCart_info)
admin.site.register(Order,Vieworder_info)

