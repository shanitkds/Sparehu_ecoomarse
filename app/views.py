from django.shortcuts import render,redirect,get_object_or_404
from .form import Registration,Login
from django.contrib import messages
from django.contrib.auth import login,logout
from .models import Product,Cart,Order,User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import stripe
from django.conf import settings
from django.urls import reverse
from django.db.models import Q

stripe.api_key=settings.STRIPE_SECRET_KEY


# Create your views here.

def home(request):
    fucher = [
        {'name': 'Heavy Duty Trucks', 'image': '1.png'},
        {'name': 'Truck Engine Parts', 'image': '2.png'},
        {'name': 'Motorcycle Engine', 'image': '3.png'},
        {'name': 'Bicycle Spare Parts ', 'image': '4.png'},
    ]
    
    brand=Product.objects.values_list('brand',flat=True).distinct()
    return render(request,'Home.html',{'brand':brand,'fucher':fucher})

def registration(request):
    form=Registration(request.POST or None)
    if request.method=='POST' and form.is_valid():
        form.save()
        messages.success(request,"Registration successful! Please login.")
        return redirect("account_login")
    return render(request,'Register.html',{'form':form})

def login_view(request):
    form = Login(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful! Welcome")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'Login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def brand_search(request):
    brand=Product.objects.values_list('brand',flat=True).distinct()
    return render(request,'BrandSearch.html',{'brand':brand})

def view_product(request,brand=None):
    query=request.GET.get('q','')
    if brand:
        products=Product.objects.filter(brand=brand)
    else:
        products=Product.objects.all()
        
    if query:
        products=products.filter(Q(name__icontains=query)|Q(brand__icontains=query))
    return render(request,'ViewProduct.html',{'products':products,'query':query})

    

def uniq_detaild(request,id):
    product=get_object_or_404(Product,id=id)
    return render(request,'UniqDetails.html',{'product':product})

@login_required
def handil_action(request,id):
    if request.method=="POST":
        action=request.POST.get('action')
        if action=='cart':
            return add_cart(request,id)
        elif action=='order':
            return direct_checkout(request,id)
            
    return redirect('home')
# -----------------------------------------------
@login_required
def add_cart(request,id):
    product=get_object_or_404(Product,id=id)
    quantity=int(request.POST.get('quantity',1))
    cart_item,created=Cart.objects.get_or_create(user=request.user,product=product)
    if not created:
        cart_item.quantity+=quantity
        cart_item.save()
        messages.info(request, "Product quantity updated in cart")
    else:
        messages.success(request,"Product added to cart successfully")
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def view_cart(request):
    total=0
    products=Cart.objects.filter(user=request.user)
    for i in products:
        total+=i.product.price*i.quantity
    return render(request,'ViewCart.html',{'products':products,'total':total})

def remove(request,id):
    product=get_object_or_404(Cart,user=request.user,id=id)
    if product.quantity>1:
        product.quantity-=1
        product.save()
    else:
        product.delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))

def order_now(request,id):
    item=get_object_or_404(Product,id=id)
    quantity=int(request.session.pop('quantity',1))
    request.session.pop('quantity',None)
    
    print(request.user)
    print(quantity)
    print(request.POST.get('adress'))
    price=quantity*item.price
   
    
    session=stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data':{
                    'currency':'inr',
                    'product_data':{
                        'name':item.name
                    },
                    'unit_amount':int(float(item.price)*100),
                },
                'quantity':quantity,
            }
        ],
        mode='payment',
        success_url=request.build_absolute_uri(reverse('payment_susses'))+ '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri(reverse('view_cart')),
        metadata={
            'user_id':str(request.user),
            'product':str(id),
            'address':request.POST.get('adress'),
            'type':'direct',
            'quantity':quantity
        },
        
    )
    
    return redirect(session.url)
# -----------
def buy_from_cart(request,id=None):
    # susses=False
    # checkout_items=request.session.get('checkout_items',[])
    if id:
        cart_item=Cart.objects.filter(user=request.user,product_id=id)
    else:
        cart_item=Cart.objects.filter(user=request.user)
    if not cart_item.exists():
        return redirect
    
    all_items=[]
    
    for item in cart_item:
        all_items.append({
            'price_data':{
                'currency':'inr',
                'product_data':{
                    'name':item.product.name,
                },
                'unit_amount':int(float(item.product.price)*100)
            },
            'quantity':item.quantity
        })
    session=stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=all_items,
        mode='payment',
        success_url=request.build_absolute_uri(reverse('payment_susses'))+ '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri(reverse('view_cart')),
        metadata={
            'user_id':str(request.user),
            'product':str(id) if id else 'all',
            'address':request.POST.get('adress'),
            'type':'cart'
        }
        

        
    )
    
    return redirect(session.url)




def payment_susses(request):
    session_id=request.GET.get('session_id')
    
    if not session_id:
        return redirect("view_cart")
    
    session = stripe.checkout.Session.retrieve(session_id)
    address=session.metadata.get('address')
    product_id=session.metadata.get('product')
    type=session.metadata.get('type')
    
    
    
    if type=='cart':
        if product_id != 'all':
            cart_item=Cart.objects.filter(user=request.user,product_id=product_id)
        else:
            cart_item=Cart.objects.filter(user=request.user)
        
        for item in cart_item:
         Order.objects.create(
         user=request.user,
         product=item.product,
         quantity=item.quantity,
         address=address,
         payment_methd="Debit" 
        )
    
        cart_item.delete()
    elif type=="direct":
        quantity=session.metadata.get('quantity')
        cart_item=get_object_or_404(Product,id=product_id)
        Order.objects.create(
         user=request.user,
         product=cart_item,
         quantity=quantity,
         address=address,
         payment_methd="Debit" 
        )
    return render(request,'SussesPage.html')


def cart_checkout(request,id=None):
    totalprice=0
    if id:
        cart_item=Cart.objects.filter(user=request.user,product_id=id)
        mult=False
        item_id=id
    else:
        cart_item=Cart.objects.filter(user=request.user) 
        mult=True
        item_id=None
    for i in cart_item:
        totalprice+=i.product.price*i.quantity
    request.session['checkout_type']='cart'
    checkout='cart'
    
    return render(request,'Checkout.html',{'item':cart_item,'totalprice':totalprice,'item_id':item_id,'checkout':checkout})


@login_required
def direct_checkout(request,id):
    if not id:
        return redirect('home')
    item_id=id
    quantity=int(request.POST.get('quantity',1))
    item=get_object_or_404(Product,id=id)
    totalprice=quantity*item.price
    request.session['checkout_type']='direct'
    request.session['quantity']=quantity
    checkout='direct'
    return render(request,'Checkout.html',{'item':item,'totalprice':totalprice,'item_id':item_id,'quantity':quantity,'checkout':checkout})
    


@login_required
def payment_root(request,id=None):
    checkout=request.session.get('checkout_type')
    request.session.pop('checkout_type',None)
    paymentType=request.POST.get('payment_type')
    if paymentType=='cod':
        return cod_payment_susses(request,checkout,id)
    elif paymentType=='online':
        if checkout=='cart':
            return buy_from_cart(request,id)
        else:
            return order_now(request,id)
    
def cod_payment_susses(request,checkout,id=None):
    if checkout=='cart':
        if id:
            buy_item=Cart.objects.filter(user=request.user,product_id=id)
        else:
            buy_item=Cart.objects.filter(user=request.user)
    elif checkout=='direct':
        buy_item=get_object_or_404(Product,id=id)
        quantity=request.session.get('quantity')
        request.session.pop('quantity',None)
        print(quantity)
    else:
        return redirect('home')
    
    
    if checkout=='cart':   
        for item in buy_item:
            Order.objects.create(
                user=request.user,
                product=item.product,
                quantity=item.quantity,
                address=request.POST.get('adress'),
                payment_methd="COD"
            )
        buy_item.delete()
    else:
        Order.objects.create(
                user=request.user,
                product=buy_item,
                quantity=quantity,
                address=request.POST.get('adress'),
                payment_methd="COD"
            )
    return render(request,'SussesPage.html')

@login_required
def profile(request):
    return render(request,'Profile.html')

@login_required
def profileupdate(request,id):
    user = request.user
    userInfo=Registration(request.POST or None,instance=user)
    if request.method=='POST':
        if userInfo.is_valid():
            userInfo.save()
            messages.success(request, "Yor Profile Uodated")
            return redirect("Profile")
        else:
            messages.error(request, "Try Again")
        
    return render(request,'EditUser.html',{'form':userInfo})

@login_required
def myordars(request):
    try:
        ordars=Order.objects.filter(user=request.user)
    except Exception:
        messages.error(request, "Something went wrong. Please try again.")
        print(Exception)
        ordars=[]
    
    return render(request,'Orders.html',{'ordars':ordars})


    
# -------------------------------------------------------------------------------

# @login_required
# def Checkout(request,buy_type='cart',id=None):
#     item=[]
#     totalprice=0
#     type=''
#     print(buy_type)
   

#     if buy_type=='dirrect':
#         type='dirrect'
#         product=get_object_or_404(Product,id=id)
#         quantity=int(request.POST.get('quantity',1))
#         item.append({
#             'product':product,
#             'quantity':quantity,
#         })
#         # request.session['checkout_items']=[{'product_id':product.id,'quantity':quantity,'type':'dirrect'}]
#     elif buy_type=='cart':
#         type='cart'
#         if id:
#             cart_item=Cart.objects.filter(user=request.user,product_id=id)
#             request.session['checkout_items']=None
#         else:
#             cart_item=Cart.objects.filter(user=request.user)
#         for cart in cart_item:
#             item.append({
#                 'product':cart.product,
#                 'quantity':cart.quantity,
#             })
#             # request.session['checkout_items']=[{"product_id":i['product'].id,} for i in item]
            
#     for i in item:
#         totalprice+=i['product'].price*i['quantity']
        
#     # request.session['checkout_items']=[{"id":i['product'].id} for i in item]
#     request.session['type']=type    
#     return render(request,'Checkout.html',{'item':item,'totalprice':totalprice})
    
# --------------------------------------------------------------------


        
    
    
# def cod_payment_susses(request):             #IT IS COD SUSSES 
#     type=request.session.get('type')
#     checkout_items=request.session.get('checkout_items',[])
#     print(checkout_items)
#     print(type)
#     if type=='cart':
#         # for item in checkout_items:
#         #     product=Cart.objects.get(user=request.user,product_id=item['product_id'])
#         #     Order.objects.create(
#         #         user=request.user,
#         #         product=product.product,
#         #         quantity=product.quantity,
#         #         address=request.POST.get('adress'),
#         #         payment_methd="COD"
#         #     )
#         # ----------------------------------------------------------------------------------------
#         if not checkout_items:
#             product=Cart.objects.filter(user=request.user)
#             for item in product:
#                 Order.objects.create(
#                 user=request.user,
#                 product=product.product,
#                 quantity=product.quantity,
#                 address=request.POST.get('adress'),
#                 payment_methd="COD"
#             )
            
#     elif type=='dirrect':
#         id=checkout_items[0]['product_id']
#         quantity=request.session.get('quantity')
#         product=Product.objects.get(user=request.user,id=id)
#         Order.objects.create(
#                 user=request.user,
#                 product=product.product,
#                 quantity=quantity,
#                 address=request.POST.get('adress'),
#                 payment_methd="COD"
#             )
            
            
#     return render(request,'SussesPage.html')
