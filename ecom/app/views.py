from django.db.models import Count , Q
from django.http import JsonResponse
from django.shortcuts import render , redirect
from django.views import View
from . models import Product, Customer, Cart, Payment, OrderPlaced, Wishlist, BuyNow
from . forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.conf import settings
import razorpay
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, get_object_or_404

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
@method_decorator(login_required,name='dispatch')
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

# Mobiles
def mobiles(request, data = None):
    if data == None:
        mobiles = Product.objects.filter(category='M')
    elif data == 'Apple' or data == 'Redmi' or data == 'Oneplus':
        mobiles = Product.objects.filter(category='M').filter(brand=data)
    elif data == 'below':
        mobiles = Product.objects.filter(category='M').filter(discounted_price__lt=20000)
    elif data == 'above':
        mobiles = Product.objects.filter(category='M').filter(discounted_price__gt=20000)
    return render(request, 'app/mobiles.html',{'mobiles':mobiles})

# Laptops
def laptops(request, data = None):
    if data == None:
        laptops = Product.objects.filter(category='L')
    elif data == 'Asus' or data == 'Acer' or data == 'Lenovo':
        laptops = Product.objects.filter(category='L').filter(brand=data)
    elif data == 'below':
        laptops = Product.objects.filter(category='L').filter(discounted_price__lt=50000)
    elif data == 'above':
        laptops = Product.objects.filter(category='L').filter(discounted_price__gt=50000)
    return render(request, 'app/laptops.html',{'laptops':laptops})

# menswear
def menswear(request, data = None):
    if data == None:
        menswear = Product.objects.filter(category='MW')
    elif data == 'Shirts' or data == 'T-Shirts' or data == 'Suits':
        menswear = Product.objects.filter(category='MW').filter(brand=data)
    elif data == 'below':
        menswear = Product.objects.filter(category='MW').filter(discounted_price__lt=1000)
    elif data == 'above':
        menswear = Product.objects.filter(category='MW').filter(discounted_price__gt=1000)
    return render(request, 'app/menswear.html',{'menswear':menswear})

# Womenswear
def womenswear(request, data = None):
    if data == None:
        womenswear = Product.objects.filter(category='WW')
    elif data == 'Sarees' or data == 'Kurtis' or data == 'Tops':
        womenswear = Product.objects.filter(category='WW').filter(brand=data)
    elif data == 'below':
        womenswear = Product.objects.filter(category='WW').filter(discounted_price__lt=1000)
    elif data == 'above':
        womenswear = Product.objects.filter(category='WW').filter(discounted_price__gt=1000)
    return render(request, 'app/womenswear.html',{'womenswear':womenswear})


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
            return redirect("login")
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
            return redirect("address")
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


def buy_now(request, pk):
    print("Buy Now view triggered")
    product = get_object_or_404(Product, pk=pk)
    print(f"Product: {product}")
    user = request.user
    
    # Check if the user already has a BuyNow item and delete it (only one Buy Now item allowed at a time)
    BuyNow.objects.filter(user=request.user).delete()
    
    # Add product to Buy Now database for the current user
    buy_now_item = BuyNow(user=request.user, product=product, quantity=1)
    buy_now_item.save()
     
    print(f"Buy Now item saved: {buy_now_item}")

    # Redirect to the checkout page after the product is added to buy_now
    return redirect('/checkout/?buy_now=true')
    # return render(request, 'app/buynow.html')


@login_required
def add_to_cart(request):
    user = request.user
    # print("user: ", user)
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    # print("product: ",product)
    Cart(user=user,product=product).save()
    # print("cart: ",Cart)
    return redirect('/cart')

@login_required
def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    if not cart.exists():
        return render(request, 'app/empty.html')  # Redirect to an empty cart page if no items are in the cart
    # print("cart: ",cart)
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

# @method_decorator(login_required,name='dispatch')
# class checkout(View):
#     def get(self,request):
#         totalitem = 0
#         wishitem = 0
#         if request.user.is_authenticated:
#             totalitem = len(Cart.objects.filter(user=request.user))
#             wishitem = len(Wishlist.objects.filter(user=request.user))
#         user=request.user
#         add=Customer.objects.filter(user=user)
#         cart_items=Cart.objects.filter(user=user)
#         famount= 0 
#         for p in cart_items:
#             value = p.quantity * p.product.discounted_price
#             famount = famount + value
#         totalamount = famount + 40
#         # Handle Razorpay payments
#         razoramount = int(totalamount * 100)  
#         client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
#         # print("client: ",client) 
#         data = {"amount": razoramount, "currency":"INR", "receipt":"order_rcptid_12"}
#         payment_response = client.order.create(data=data)

#         # {'id': 'order_NmbqrK3DfEeo0j', 'entity': 'order', 'amount': 64500, 'amount_paid': 0, 'amount_due': 64500, 'currency': 'INR', 'receipt': 'order_rcptid_12', 'offer_id': None, 'status': 'created', 'attempts': 0, 'notes': [], 'created_at': 1710501017}

#         order_id = payment_response['id']
#         order_status = payment_response['status']
#         if order_status == 'created':
#             payment = Payment(
#                 user = user,
#                 amount = totalamount,
#                 razorpay_order_id = order_id,
#                 razorpay_payment_status = order_status
#             )
#             payment.save()
#             print("payment: ", payment)

#          # Add this code block for COD handling
#         if request.GET.get('payment_mode') == 'COD':
#             payment = Payment(
#                 user=user,
#                 amount=totalamount,
#                 razorpay_order_id='COD',
#                 razorpay_payment_status='COD',
#                 paid=True
#             )
#             payment.save()
#             print(" cod payment: ",payment)
#             for item in cart_items:
#                 OrderPlaced(user=user, customer=item.user.customer_set.first(), product=item.product, quantity=item.quantity, payment=payment).save()
#                 item.delete()

#             return redirect('orders')

#         return render(request,'app/checkout.html',locals())


# @login_required
# def payment_done(request):
#     order_id = request.GET.get('order_id')  
#     print("order_id: ",order_id)
#     payment_id = request.GET.get('payment_id')
#     print("payment_id: ",payment_id)
#     cust_id = request.GET.get('cust_id')
#     print("custid: ",cust_id)
#     # print("payment_done : old = ",order_id,"pid = ",payment_id,"cid = ",cust_id)
    
#     if order_id != 'COD':
#         user = request.user
#         customer = Customer.objects.get(id=cust_id)
#         print("customer: ", customer)
#         cart = Cart.objects.filter(user=user)
#         print("payment_done_cart: ",cart)
#         payment = Payment.objects.get(razorpay_order_id=order_id)
#         payment.paid = True
#         payment.razorpay_payment_id = payment_id
#         payment.save()
#         print("payment details: ",payment)
#         cart = Cart.objects.filter(user=user)
#         print("payment_done_cart: ",cart)
#         for c in cart:
#             OrderPlaced(user=user,customer=customer,product=c.product,quantity=c.quantity,payment=payment).save()
#             print(f"Order Created: User: {user}, Product: {c.product}")
#             c.delete()

#      # Handle Cash on Delivery (COD)
#     else:
#         user = request.user
#         customer = Customer.objects.get(id=cust_id)
#         cart = Cart.objects.filter(user=user)
#         payment = Payment.objects.create(
#             user=user,
#             amount=0,  # You can set a dummy amount here since it's COD
#             paid=False,  # Payment is not yet completed
#             payment_method='COD'
#         )
#         for c in cart:
#             OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity, payment=payment).save()
#             c.delete()  # Clear the cart after placing the order
#     # print("Redirecting to orders page")
#     return redirect("orders")
 

# @method_decorator(login_required, name='dispatch')
# class checkout(View):
#     def get(self, request):
#         totalitem = 0
#         wishitem = 0
#         if request.user.is_authenticated:
#             totalitem = len(Cart.objects.filter(user=request.user))
#             wishitem = len(Wishlist.objects.filter(user=request.user))

#         user = request.user
#         add = Customer.objects.filter(user=user)
#         cart_items = Cart.objects.filter(user=user)
#         buy_now_item = BuyNow.objects.filter(user=user).first()  # Only one item for Buy Now

#         famount = 0

#         if buy_now_item:
#             # If it's a Buy Now flow, calculate the amount for that item only
#             famount = buy_now_item.quantity * buy_now_item.product.discounted_price
#             totalamount = famount + 40  # Add shipping cost
#         else:
#             # For cart items
#             for p in cart_items:
#                 value = p.quantity * p.product.discounted_price
#                 famount += value
#             totalamount = famount + 40  # Add shipping cost

#         # Handle Razorpay payments
#         razoramount = int(totalamount * 100)
#         client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
#         data = {"amount": razoramount, "currency": "INR", "receipt": "order_rcptid_12"}
#         payment_response = client.order.create(data=data)
#         order_id = payment_response['id']
#         order_status = payment_response['status']

#         if order_status == 'created':
#             payment = Payment(
#                 user=user,
#                 amount=totalamount,
#                 razorpay_order_id=order_id,
#                 razorpay_payment_status=order_status
#             )
#             payment.save()

#         # Handle Cash on Delivery (COD) logic
#         if request.GET.get('payment_mode') == 'COD':
#             payment = Payment(
#                 user=user,
#                 amount=totalamount,
#                 razorpay_order_id='COD',
#                 razorpay_payment_status='COD',
#                 paid=True
#             )
#             payment.save()

#             if buy_now_item:
#                 # Place order for Buy Now item
#                 OrderPlaced(user=user, customer=buy_now_item.user.customer_set.first(), product=buy_now_item.product,
#                             quantity=buy_now_item.quantity, payment=payment).save()
#                 buy_now_item.delete()  # Clear Buy Now item
#             else:
#                 # Place orders for cart items
#                 for item in cart_items:
#                     OrderPlaced(user=user, customer=item.user.customer_set.first(), product=item.product,
#                                 quantity=item.quantity, payment=payment).save()
#                     item.delete()

#             return redirect('orders')

#         return render(request, 'app/checkout.html', locals())


@method_decorator(login_required, name='dispatch')
class checkout(View):
    def get(self, request):
        totalitem = 0
        wishitem = 0
        buy_now_flag = request.GET.get('buy_now', None)  # Check if 'buy_now' flag is passed in the URL
        print("buy_now_flag: ",buy_now_flag)

        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))

        user = request.user
        add = Customer.objects.filter(user=user)  # User address information
        print("Addresses: ", add)

        cart_items = None
        buy_now_item = None
        famount = 0
        
        # Check if the user is checking out with 'Buy Now' or 'Cart'
        if buy_now_flag:  # If 'buy_now' flag is set
            buy_now_item = BuyNow.objects.filter(user=user).first()  # Fetch the Buy Now item
            print("buy_now_item:",buy_now_item)
            if buy_now_item:
                famount = buy_now_item.quantity * buy_now_item.product.discounted_price
                totalamount = famount + 40  # Add shipping cost
        else:
            cart_items = Cart.objects.filter(user=user)  # Fetch cart items if no 'buy_now' flag
            for p in cart_items:
                value = p.quantity * p.product.discounted_price
                famount += value
        totalamount = famount + 40  # Add shipping cost

        # Razorpay integration for payment
        razoramount = int(totalamount * 100)
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        data = {"amount": razoramount, "currency": "INR", "receipt": "order_rcptid_12"}
        payment_response = client.order.create(data=data)
        order_id = payment_response['id']
        order_status = payment_response['status']

        if order_status == 'created':
            payment = Payment(
                user=user,
                amount=totalamount,
                razorpay_order_id=order_id,
                razorpay_payment_status=order_status
            )
            payment.save()

        # If 'Cash on Delivery' is selected
        if request.GET.get('payment_mode') == 'COD':
            payment = Payment(
                user=user,
                amount=totalamount,
                razorpay_order_id='COD',
                razorpay_payment_status='COD',
                paid=True
            )
            payment.save()

            # If 'Buy Now' was clicked, place the order for that item
            if buy_now_flag and buy_now_item:
                OrderPlaced(user=user, customer=buy_now_item.user.customer_set.first(), product=buy_now_item.product, quantity=buy_now_item.quantity, payment=payment).save()
                print("Buy now OrderPlaced: ",)
                buy_now_item.delete()  # Clear the Buy Now item after placing the order

            # If the checkout is for cart items, place the order for all cart items
            else:
                for item in cart_items:
                    OrderPlaced(user=user, customer=item.user.customer_set.first(), product=item.product, quantity=item.quantity, payment=payment).save()
                    item.delete()  # Clear cart after placing the order

            return redirect('orders')
            # add = Customer.objects.filter(user=user)

             # Build context dictionary
        context = {
            'totalitem': totalitem,
            'wishitem': wishitem,
            'buy_now_flag': buy_now_flag,
            'add': add,
            'cart_items': cart_items,
            'buy_now_item': buy_now_item,
            'totalamount': totalamount,
            'razoramount': razoramount,
            'order_id': order_id,
        }
        print("Addresses in context: ", add)

        return render(request, 'app/checkout.html', context)



@login_required
def payment_done(request):
    order_id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id')
    cust_id = request.GET.get('cust_id')

    if order_id != 'COD':
        user = request.user
        customer = Customer.objects.get(id=cust_id)
        buy_now_item = BuyNow.objects.filter(user=user).first()  # Handle Buy Now item
        cart_items = Cart.objects.filter(user=user)  # Handle Cart items
        payment = Payment.objects.get(razorpay_order_id=order_id)
        payment.paid = True
        payment.razorpay_payment_id = payment_id
        payment.save()

        if buy_now_item:
            # Place order for Buy Now item
            OrderPlaced(user=user, customer=customer, product=buy_now_item.product, quantity=buy_now_item.quantity,
                        payment=payment).save()
            buy_now_item.delete()  # Clear the Buy Now item
        else:
            # Place orders for cart items
            for c in cart_items:
                OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity, payment=payment).save()
                c.delete()  # Clear cart items after placing order
    else:
        # Handle Cash on Delivery (COD)
        user = request.user
        customer = Customer.objects.get(id=cust_id)
        buy_now_item = BuyNow.objects.filter(user=user).first()
        cart_items = Cart.objects.filter(user=user)

        payment = Payment.objects.create(
            user=user,
            amount=0,  # Set a dummy amount here since it's COD
            paid=False,
            payment_method='COD'
        )

        if buy_now_item:
            # Place order for Buy Now item
            OrderPlaced(user=user, customer=customer, product=buy_now_item.product, quantity=buy_now_item.quantity,
                        payment=payment).save()
            buy_now_item.delete()  # Clear the Buy Now item
        else:
            # Place orders for cart items
            for c in cart_items:
                OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity, payment=payment).save()
                c.delete()  # Clear the cart after placing the order

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