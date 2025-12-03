from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Products, Order, OrderItem, Review
from django.db.models import Q
from django.shortcuts import redirect
from .forms import ReviewForm
from django.db import models
import uuid


from .cart import Cart
from .forms import OrderForm, StoreForm

from userprofile.models import Userprofile  # if you still use Userprofile


from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import StoreForm

from django.contrib import messages

# store/views.py
def vendor_success(request):
    return render(request, "store/vendor_success.html")





from django.db import IntegrityError

def product_detail(request, product_id):
    product = get_object_or_404(Products, id=product_id)

    # Increment product views
    product.views_count += 1
    product.save(update_fields=['views_count'])

    cart = Cart(request)
    form = ReviewForm()
    reviews = product.reviews.all()
    avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']

    # 🟢 Get related products from the same category (excluding the current one)
    related_products = Products.objects.filter(category=product.category, quantity__gt=0).exclude(id=product.id)[:4]

    # Handle review submission
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            try:
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                messages.success(request, "Your review has been submitted successfully.")
            except IntegrityError:
                # If user already reviewed, update instead of crashing
                existing_review = product.reviews.filter(user=request.user).first()
                if existing_review:
                    existing_review.rating = form.cleaned_data.get('rating')
                    existing_review.comment = form.cleaned_data.get('comment')
                    existing_review.save()
                    messages.info(request, "Your review has been updated.")
            return redirect('product_detail', product_id=product.id)

    return render(request, 'store/product_detail.html', {
        'product': product,
        'cart': cart,
        'form': form,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'related_products': related_products,  # ✅ send related products to template
    })




def add_to_cart(request, product_id):
    cart = Cart(request)
    cart.add(product_id)

    return redirect('frontpage')

def cart_view(request):
	cart = Cart(request)

	return render(request, 'store/cart_view.html', { 'cart':cart } )


def get_total_cost(self):
	for p in self.cart.keys():
		self.cart[str(p)]['product'] = Product.objects.get(pk=p)

	return int(sum(item['product'].price * item['quantity'] for item in self.cart.values()))

def clear(self):
	del self.session[settings.CART_SESSION_ID]
	self.session.modified = True

def change_quantity(request, product_id):
	action = request.GET.get('action', '')

	if action:
		quantity = 1
		if action == 'decrease':
			quantity = -1
		else:
			if action == 'increase':
				quantity = +1
		cart = Cart(request)
		cart.add(product_id, quantity, True)



	return redirect('cart_view')


def remove_from_cart(request, product_id):
	cart = Cart(request)
	cart.remove(product_id)

	return redirect('cart_view')

from django.conf import settings
import requests

@login_required
def checkout(request):
    cart = Cart(request)

    if len(cart) == 0:
        return render(request, 'store/checkout.html', {
            'cart': cart,
            'error': 'Your cart is empty.'
        })

    total_price = 0
    for item in cart:
        product = item['product']
        total_price += product.price * int(item['quantity'])

    # IMPORTANT FIX: Do NOT create order yet.
    # Only generate a ref for Flutterwave
    tx_ref = f"TX-{uuid.uuid4().hex[:10]}"

    payload = {
        "tx_ref": tx_ref,
        "amount": str(total_price),
        "currency": "ZMW",
        "redirect_url": request.build_absolute_uri('/payment/callback/'),
        "customer": {
            "email": "noemail@easyaccess.com",
            "name": request.user.username,
            "phonenumber": "260977000000"
        },
        "payment_options": "mobilemoneyzambia",
        "customizations": {
            "title": "Easy Access Payment",
            "description": f"Payment for Cart",
            "logo": "https://your-domain.com/static/images/logo.png"
        }
    }

    headers = {
        "Authorization": f"Bearer {settings.FLW_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post("https://ravesandboxapi.flutterwave.com/v3/payments",
                             json=payload, headers=headers)
    data = response.json()

    print("FLUTTERWAVE RESPONSE:", data)

    if data.get('status') == 'success' and data['data'].get('link'):
        # Redirect user to Flutterwave
        # Store tx_ref in session so we can connect it later
        request.session['tx_ref'] = tx_ref
        return redirect(data['data']['link'])
    else:
        return render(request, 'store/checkout.html', {
            'cart': cart,
            'error': 'Payment initialization failed. Please try again later.'
        })




import requests
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .cart import Cart
from .models import Order
@login_required
def payment_callback(request):
    status = request.GET.get('status')
    tx_ref = request.session.get('tx_ref')
    transaction_id = request.GET.get('transaction_id')

    if status != 'successful':
        messages.error(request, "Payment failed or was cancelled.")
        return redirect('cart_view')

    # Verify with Flutterwave
    verify_url = f"https://ravesandboxapi.flutterwave.com/v3/transactions/{transaction_id}/verify"
    headers = {
        "Authorization": f"Bearer {settings.FLW_SECRET_KEY}",
    }

    response = requests.get(verify_url, headers=headers)
    data = response.json()

    if data.get('status') == 'success' and data['data']['status'] == 'successful':
        cart = Cart(request)

        # FINAL FIX: Create order NOW only after successful payment
        total_price = 0
        for item in cart:
            product = item['product']
            total_price += product.price * int(item['quantity'])

        order = Order.objects.create(
            created_by=request.user,
            paid_amount=total_price,
            is_paid=True
        )

        for item in cart:
            product = item['product']
            quantity = int(item['quantity'])
            price = product.price * quantity

            OrderItem.objects.create(
                order=order,
                product=product,
                price=price,
                quantity=quantity
            )

        # Clear cart only after success
        cart.clear()
        request.session.pop('tx_ref', None)

        messages.success(request, "Payment successful! Your order has been placed.")
        return redirect('myaccount')

    messages.error(request, "Payment verification failed. Please contact support.")
    return redirect('cart_view')


from django.db.models import Q, F
from django.db.models.functions import Sqrt, Power

from django.db.models import Q, F
from django.db.models.functions import Sqrt, Power
from django.shortcuts import render

def search(request):
    query = request.GET.get('query', '')

    products = Products.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(category__title__icontains=query),
        status=Products.ACTIVE
    )

    # Distance sorting (only if user has location)
    user = request.user
    if user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.latitude:
        user_lat = user.userprofile.latitude
        user_lon = user.userprofile.longitude

        products = products.annotate(
            distance=Sqrt(
                Power(F('latitude') - user_lat, 2) +
                Power(F('longitude') - user_lon, 2)
            )
        ).order_by('distance')

    return render(request, 'store/search.html', {
        'products': products,
        'query': query
    })







@login_required
def my_store_order_detail(request, pk):
	order = get_object_or_404(Order, pk=pk)
	return render(request, 'userprofile/my_store_order_detail.html', {'order': order})

