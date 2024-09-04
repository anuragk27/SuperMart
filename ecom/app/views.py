from django.db.models import Count , Q
from django.http import JsonResponse
from django.shortcuts import render , redirect
from django.views import View
from . models import Product, Customer, Cart, Payment, OrderPlaced, Wishlist
from . forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.conf import settings
import razorpay
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Create your views here.
def home(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))

 #ref   
    mobiles = Product.objects.filter(category='M')
    laptops = Product.objects.filter(category='L')
    menswear = Product.objects.filter(category='MW')
    womenswear = Product.objects.filter(category='WW')
    return render(request,"app/home.html",{
        'mobiles': mobiles,
        'laptops': laptops,
        'menswear': menswear,
        'womenswear': womenswear,
        'totalitem': totalitem,
        'wishitem': wishitem
    })

@login_required
def about(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request,"app/about.html",locals())

@login_required  # for functions
def contact(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request,"app/contact.html",locals())

@method_decorator(login_required,name='dispatch') 
class CategoryView(View):
    def get(self,request,val):
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))

        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title')
        return render(request,"app/category.html",locals())

@method_decorator(login_required,name='dispatch')
class CategoryTitle(View):
    def get(self,request,val):
        product = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0].category).values('title')
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request,"app/category.html",locals())

# ref
# class ProductView(View):
#     def get(self,request):
#         mobiles = Product.objects.filter(category='M')
#         Laptops = Product.objects.filter(category='L')
#         Menswear = Product.objects.filter(category='MW')
#         Womenswear = Product.objects.filter(category='WW')
#         return render(request, 'app/home.html',{'mobiles':mobiles, 'Laptops':Laptops,
#          'Menswear':Menswear, 'Womenswear':Womenswear})

# ref
class ProductDetail(View):
    def get(self,request,pk):
        product = Product.objects.get(pk=pk)
        wishlist = Wishlist.objects.filter(Q(product=product) & Q(user=request.user))
        totalitem = 0
        wishitem = 0 
        item_already_in_cart = False
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
            item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user) ).exists()
        return render(request, 'app/productdetail.html',{'product':product, 'item_already_in_cart':item_already_in_cart,'totalitem': totalitem,
        'wishlist':wishlist,'wishitem': wishitem})

# ref
def mobile(request, data = None):
    if data == None:
        mobiles = Product.objects.filter(category='M')
    elif data == 'Apple' or data == 'Redmi' or data == 'Oneplus':
        mobiles = Product.objects.filter(category='M').filter(brand=data)
    elif data == 'below':
        mobiles = Product.objects.filter(category='M').filter(discounted_price__lt=50)
    elif data == 'above':
        mobiles = Product.objects.filter(category='M').filter(discounted_price__gt=50)
    return render(request, 'app/mobile.html',{'mobiles':mobiles})


# @method_decorator(login_required,name='dispatch')
# class ProductDetail(View):
#     def get(self,request,pk):
#         product = Product.objects.get(pk=pk)
#         wishlist = Wishlist.objects.filter(Q(product=product) & Q(user=request.user))
#         totalitem = 0
#         wishitem = 0 
#         if request.user.is_authenticated:
#             totalitem = len(Cart.objects.filter(user=request.user))
#             wishitem = len(Wishlist.objects.filter(user=request.user))
#         return render(request,"app/productdetail.html",locals())      


class CustomerRegistrationView(View):
    def get(self,request):
        form=CustomerRegistrationForm()
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user)) 
        return render(request,'app/customerregistration.html',locals())
    def post(self,request):
        form=CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Congratulations!User Register Successfull")
        else:
            messages.warning(request,"Invalid Input Data")
        return render(request,'app/customerregistration.html',locals())

@method_decorator(login_required,name='dispatch')
class ProfileView(View):
    def get(self,request):
        form = CustomerProfileForm()
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user)) 
        return render(request,'app/profile.html',locals())

    def post(self,request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            print("user: ",user)
            name = form.cleaned_data['name']
            print("name:",name)
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']

            reg =Customer(user=user,name=name,locality=locality,city=city,mobile=mobile,state=state,
            zipcode = zipcode)
            reg.save()
            messages.success(request,"Congratulations! Profile Save Successfully ")
        else:
            messages.warning(request,"Invalid Input Data")
        return render(request,'app/profile.html',locals())

@login_required
def address(request):
    add = Customer.objects.filter(user=request.user)
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request,'app/address.html',locals())

@method_decorator(login_required,name='dispatch')
class updateAddress(View):
    def get(self,request,pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add) #by this, the update fields will be filled already
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request,'app/updateAddress.html',locals())
    def post(self,request,pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request,"Congratulations! Profile Update Successfully ")
        else:
            messages.warning(request,"Invalid Input Data")
        return redirect("address")   #redirect error so import redirect

@login_required
def add_to_cart(request):
    user = request.user
    print("user: ", user)
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    print("product: ",product)
    Cart(user=user,product=product).save()
    print("cart: ",Cart)
    return redirect('/cart')

@login_required
def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    print("cart: ",cart)
    amount = 0
    for p in cart:
        value = p.quantity * p.product.discounted_price
        amount = amount + value
    totalamount = amount + 40
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    
    return render(request,'app/addtocart.html',locals())

@login_required
def show_wishlist(request):
    user = request.user
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    product = Wishlist.objects.filter(user=user)
    return render(request,'app/wishlist.html',locals())

@method_decorator(login_required,name='dispatch')
class checkout(View):
    def get(self,request):
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        user=request.user
        add=Customer.objects.filter(user=user)
        cart_items=Cart.objects.filter(user=user)
        famount= 0 
        for p in cart_items:
            value = p.quantity * p.product.discounted_price
            famount = famount + value
        totalamount = famount + 40
        razoramount = int(totalamount * 100)  
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        print("client: ",client)
        data = {"amount": razoramount, "currency":"INR", "receipt":"order_rcptid_12"}
        payment_response = client.order.create(data=data)
        print(payment_response)

        # {'id': 'order_NmbqrK3DfEeo0j', 'entity': 'order', 'amount': 64500, 'amount_paid': 0, 'amount_due': 64500, 'currency': 'INR', 'receipt': 'order_rcptid_12', 'offer_id': None, 'status': 'created', 'attempts': 0, 'notes': [], 'created_at': 1710501017}

        order_id = payment_response['id']
        order_status = payment_response['status']
        if order_status == 'created':
            payment = Payment(
                user = user,
                amount = totalamount,
                razorpay_order_id = order_id,
                razorpay_payment_status = order_status
            )
            payment.save()
            print(payment)
        return render(request,'app/checkout.html',locals())


@login_required
def payment_done(request):
    order_id = request.GET.get('order_id')
    print(order_id)
    payment_id = request.GET.get('payment_id')
    cust_id = request.GET.get('cust_id')
    print(cust_id)
    # print("payment_done : old = ",order_id,"pid = ",payment_id,"cid = ",cust_id)
    user = request.user
    customer = Customer.objects.get(id=cust_id)
   
    payment = Payment.objects.get(razorpay_order_id=order_id)
    payment.paid = True
    payment.razorpay_payment_id = payment_id
  
    payment.save()
    print("payment details: ",payment)
    cart = Cart.objects.filter(user=user)
    print("payment_done_cart: ",cart)
    for c in cart:
        OrderPlaced(user=user,customer=customer,product=c.product,quantity=c.quantity,payment=payment).save()
        print(f"Order Created: User: {user}, Product: {c.product}")
        c.delete()
    # print("Redirecting to orders page")
    return redirect("orders")

@login_required
def orders(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        # print(f"Authenticated user: {request.user}")
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    order_placed = OrderPlaced.objects.filter(user=request.user)
    print("order_placed: ",order_placed)
    return render(request, 'app/orders.html',{'totalitem':totalitem,'wishitem':wishitem,'order_placed':order_placed})


def plus_cart(request):
     if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity+=1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount
        }
        return JsonResponse(data)

def minus_cart(request):
     if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity-=1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount
        }
        return JsonResponse(data)

def remove_cart(request):
     if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        data={
            'amount':amount,
            'totalamount':totalamount
        }
        return JsonResponse(data)

def plus_wishlist(request):
    if request.method == "GET":
        prod_id = request.GET['prod_id']
        product = Product.objects.get(id=prod_id)
        user = request.user
        Wishlist(user=user,product=product).save()
        data={
            'message':'Wishlist Added Successfully ',
        }
        return JsonResponse(data)

def minus_wishlist(request):
    if request.method == "GET":
        prod_id = request.GET['prod_id']
        product = Product.objects.get(id=prod_id)
        user = request.user
        Wishlist.objects.filter(user=user,product=product).delete()
        data={
            'message':'Wishlist Removed Successfully ',
        }
        return JsonResponse(data)

@login_required
def search(request):
    query = request.GET['search']
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    product = Product.objects.filter(Q(title__icontains=query)) #double underscore
    return render(request,"app/search.html",locals())