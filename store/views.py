from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Products, Order, OrderItem, Review
from django.db.models import Q
from django.shortcuts import redirect
from .forms import ReviewForm
from django.db import models


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

	return int(sum(item['product'].price * item['quantity'] for item in self.cart.values())) / 100

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

    # ✅ Only allow checkout if there are items
    if len(cart) == 0:
        return render(request, 'store/checkout.html', {
            'cart': cart,
            'error': 'Your cart is empty.'
        })

    total_price = 0
    for item in cart:
        product = item['product']
        total_price += product.price * int(item['quantity'])

    # ✅ Automatically create order (no form)
    order = Order.objects.create(
        created_by=request.user,
        paid_amount=total_price
    )

    # ✅ Create order items
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

    # ✅ Flutterwave Payment Payload (email optional)
    payload = {
        "tx_ref": f"TX-{order.id}",
        "amount": str(total_price),
        "currency": "ZMW",
        "redirect_url": request.build_absolute_uri('/payment/callback/'),
        "customer": {
            # ✅ Use placeholder email since your users don't have one
            "email": "noemail@easyaccess.com",
            "name": request.user.username,
            "phonenumber": "260977000000"  # optional static or user field
        },
        "payment_options": "mobilemoneyzambia",
        "customizations": {
            "title": "Easy Access Payment",
            "description": f"Payment for Order #{order.id}",
            "logo": "https://your-domain.com/static/images/logo.png"
        }
    }

    headers = {
        "Authorization": f"Bearer {settings.FLW_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post("https://ravesandboxapi.flutterwave.com/v3/payments", json=payload, headers=headers)
    data = response.json()

    print("FLUTTERWAVE RESPONSE:", data)

    # ✅ If payment link generated successfully
    if data.get('status') == 'success' and data['data'].get('link'):
        cart.clear()
        return redirect(data['data']['link'])
    else:
        return render(request, 'store/checkout.html', {
            'cart': cart,
            'error': 'Payment initialization failed. Please try again later.'
        })


@login_required
def payment_callback(request):
    status = request.GET.get('status')
    tx_ref = request.GET.get('tx_ref')

    if status == 'successful':
        # You can verify payment here if needed
        messages.success(request, "Payment successful!")
    else:
        messages.error(request, "Payment failed or cancelled.")

    return redirect('myaccount')




from django.db.models import Q, F
from django.db.models.functions import Sqrt, Power

def search(request):
    query = request.GET.get('query', '')
    products = Products.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query),
        status=Products.ACTIVE
    )

    # Annotate distance if user has a location
    user = request.user
    if user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.latitude:
        user_lat = user.userprofile.latitude
        user_lon = user.userprofile.longitude

        products = products.annotate(
            distance=Sqrt(
                Power(F('latitude') - user_lat, 2) +
                Power(F('longitude') - user_lon, 2)
            )
        ).order_by('distance')  # Closest products first

    return render(request, 'store/search.html', {'products': products, 'query': query})





@login_required
def my_store_order_detail(request, pk):
	order = get_object_or_404(Order, pk=pk)
	return render(request, 'userprofile/my_store_order_detail.html', {'order': order})

