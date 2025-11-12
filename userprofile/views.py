from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from .models import Userprofile
from store.forms import ProductForm, StoreForm, OrderItemStatusForm
from store.models import Products, Category, OrderItem, Order, Store
from django.http import HttpResponseForbidden
# Create your views here.




def vendor_detail(request, pk):
	user = User.objects.get(pk=pk)
	products = user.products.filter(status=Products.ACTIVE)

	return render(request, 'userprofile/vendor_detail.html', { 'user': user, 'products': products })


def become_vendor(request):
    # Prevent multiple stores
    if hasattr(request.user, 'store'):
        messages.info(request, "You already have a store.")
        return redirect("vendor_success")  # ✅ or redirect to their store: pk=request.user.store.pk

    if request.method == "POST":
        form = StoreForm(request.POST, request.FILES)
        if form.is_valid():
            store = form.save(commit=False)
            store.owner = request.user
            store.email = store.email or request.user.email
            store.is_approved = False  # pending approval
            store.save()

            messages.success(request, "Your store application has been submitted and is awaiting approval.")
            return redirect("vendor_success")  # ✅ success page
    else:
        form = StoreForm()

    return render(request, "store/become_vendor.html", {"form": form})



@login_required
def add_product(request):
	if request.method == 'POST':

		form = ProductForm(request.POST, request.FILES)
		if form.is_valid():
			product = form.save(commit=False)
			product.user = request.user
			product.save()
			messages.success(request, 'the product was added!')
			return redirect('mystore')
	else:
		form = ProductForm()
	return render(request, 'userprofile/add_product.html', { 'form': form, 'title': ' Add product'})


@login_required
def delete_product(request, pk):
	product = Products.objects.filter(user=request.user).get(pk=pk)
	product.status = product.DELETED
	product.save()
	messages.success(request, 'the product was deleted!')

	return redirect('mystore')




@login_required
def edit_product(request, pk):
	product = Products.objects.filter(user=request.user).get(pk=pk)

	if request.method == 'POST':
		form = ProductForm(request.POST, request.FILES, instance=product)
		if form.is_valid():
			form.save()

			messages.success(request, 'the product was changed!')

			return redirect('mystore')
	else:

		form = ProductForm(instance=product)

	return render(request, 'userprofile/add_product.html', {'form': form, 'title': 'Edit product', 'product': product})


@login_required
def myaccount(request):
    # Get all orders for the logged-in user
    orders = Order.objects.filter(created_by=request.user).prefetch_related('items__product')

    for order in orders:
        order.total_price = 0
        for item in order.items.all():
            # calculate subtotal per item
            item.subtotal = item.price * item.quantity
            order.total_price += item.subtotal

    return render(request, 'userprofile/myaccount.html', {
        'orders': orders
    })



from collections import defaultdict
from django.contrib.auth.decorators import login_required
from store.models import OrderItem, Products

from django.db.models import Sum, Q
from collections import defaultdict

from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Q

from django.db.models import Sum, Q
from django.utils import timezone
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from datetime import timedelta


@login_required
def mystore(request):
    # --- Get the vendor's store ---
    try:
        store = Store.objects.get(owner=request.user)
    except Store.DoesNotExist:
        store = None

    # --- Products for this vendor ---
    products = request.user.products.exclude(status=Products.DELETED)

    # --- All order items belonging to this vendor ---
    order_items = OrderItem.objects.filter(
        product__user=request.user
    ).select_related('order', 'order__created_by', 'product')

    # --- Group items by order ---
    orders_dict = defaultdict(list)
    for item in order_items:
        orders_dict[item.order].append(item)

    underway_orders = []
    history_orders = []

    # --- Build summaries for display ---
    for order, items in orders_dict.items():
        total_price = sum(item.get_total_price() for item in items)
        order_summary = {
            'order': order,
            'items': items,
            'total_items': len(items),
            'total_price': total_price,
            'customer': order.created_by,
            'completed': all(
                item.status == OrderItem.STATUS_DELIVERED and item.received
                for item in items
            ),
        }

        if order_summary['completed']:
            history_orders.append(order_summary)
        else:
            underway_orders.append(order_summary)

    # --- Earnings Calculation ---
    now = timezone.now()

    # Total earned (all items that belong to this vendor)
    total_earned = order_items.aggregate(total=Sum('price'))['total'] or 0

    # Pending balance (delivered but not yet marked as received)
    pending_balance = order_items.filter(
        status=OrderItem.STATUS_DELIVERED,
        received=False
    ).aggregate(total=Sum('price'))['total'] or 0

    # Available balance (received = True, no time delay)
    available_balance = order_items.filter(
        status=OrderItem.STATUS_DELIVERED,
        received=True
    ).aggregate(total=Sum('price'))['total'] or 0

    # --- Update Store Balances (and save to DB) ---
    if store:
        store.total_earned = total_earned
        store.pending_balance = pending_balance
        store.available_balance = available_balance
        store.save(update_fields=['total_earned', 'pending_balance', 'available_balance'])

    # --- Pass values to template ---
    context = {
        'products': products,
        'underway_orders': underway_orders,
        'history_orders': history_orders,
        'store': store,
        'total_earned': total_earned,
        'pending_balance': pending_balance,
        'available_balance': available_balance,
    }

    return render(request, 'userprofile/mystore.html', context)



from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def pending_earnings(request):
    # Check if the user has a store
    if hasattr(request.user, 'store'):
        store = request.user.store
        pending_orders = OrderItem.objects.filter(
            vendor=store,
            order__status='delivered',
            is_paid_to_vendor=False
        )
        print(pending_orders)
        total_pending = sum(item.price * item.quantity for item in pending_orders)
    else:
        # If the user has no store, show empty results
        pending_orders = []
        total_pending = 0

    context = {
        'pending_orders': pending_orders,
        'total_pending': total_pending
    }
    return render(request, 'userprofile/pending_earnings.html', context)



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from store.models import OrderItem
from django.db.models import F, Sum, DecimalField

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from store.models import Store

@login_required
def available_balance(request):
    balance = 0
    available_orders = []

    # Check if the logged-in user has a store (vendor account)
    if hasattr(request.user, 'store'):
        store = request.user.store

        # ✅ Use the balance stored in the database
        balance = store.available_balance

        # Optionally, still show the list of unpaid orders (for reference)
        from store.models import OrderItem
        available_orders = OrderItem.objects.filter(
            vendor=store,
            status=OrderItem.STATUS_DELIVERED,
            is_paid_to_vendor=False
        )

    context = {
        'balance': balance,
        'available_orders': available_orders
    }

    return render(request, 'userprofile/avalaible_balance.html', context)


import requests
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from decimal import Decimal

from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
import requests

from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
import requests
import logging
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
import requests
import logging

logger = logging.getLogger(__name__)

@login_required
def withdraw_funds(request):
    logger.info(f"Withdrawal requested by user {request.user.id}")

    # Check if user has a store
    store = getattr(request.user, 'store', None)
    if not store:
        logger.warning("User has no store")
        messages.error(request, "You don't have a store account.")
        return redirect("available_balance")

    logger.info(f"Store found: {store.name}, available balance: {store.available_balance}")
    amount = store.available_balance

    # Check if there are funds to withdraw
    if amount <= 0:
        logger.warning("No funds to withdraw")
        messages.warning(request, "You have no available funds to withdraw.")
        return redirect("available_balance")

    # Ensure phone number is present
    if not getattr(store, 'phone_number', None):
        logger.warning("Mobile number missing for store")
        messages.error(request, "Mobile number is missing.")
        return redirect("available_balance")

    logger.info("All checks passed, preparing Flutterwave request")
    url = "https://api.flutterwave.com/v3/transfers"
    headers = {
        "Authorization": f"Bearer {settings.FLW_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    # Convert Decimal to float for JSON serialization
    data = {
        "account_bank": "MPS",  # Replace with correct mobile money provider code
        "account_number": store.phone_number,  # Mobile money number
        "amount": float(amount),  # Convert Decimal to float
        "currency": "ZMW",
        "debit_currency": "ZMW",
        "narration": f"Withdrawal for {store.name}",
        "reference": f"wd-{store.id}-{int(amount)}",
        "full_name": store.name,  # Using store name as beneficiary
        "meta": [{"MobileNumber": store.phone_number}],
    }

    logger.info(f"Flutterwave request data: {data}")

    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        logger.info("Flutterwave API called")
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response text: {response.text}")
        result = response.json()
    except Exception as e:
        logger.error(f"Error calling Flutterwave API: {str(e)}")
        messages.error(request, f"Withdrawal failed: {str(e)}")
        return redirect("available_balance")

    # Handle response
    if result.get("status") == "success":
        store.available_balance = 0
        store.save(update_fields=["available_balance"])
        messages.success(request, f"Withdrawal of K{amount} sent successfully!")
        logger.info("Withdrawal successful, balance updated")
    else:
        msg = result.get("message") or result.get("data", {}).get("complete_message", "Unknown error")
        messages.error(request, f"Withdrawal failed: {msg}")
        logger.warning(f"Withdrawal failed: {msg}")

    return redirect("available_balance")










from .forms import UserProfileForm


@login_required
def edit_profile(request):
    profile = request.user.userprofile
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('mystore')  # Or wherever you want to redirect
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'userprofile/edit_profile.html', {'form': form})





@login_required
def order_detail(request, order_id):
    # Get the order
    order = get_object_or_404(Order, id=order_id)

    # Get only the order items belonging to this vendor
    order_items = OrderItem.objects.filter(
        order=order,
        product__user=request.user
    ).select_related('product')

    # Handle status update form
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        order_item = get_object_or_404(OrderItem, id=item_id, product__user=request.user)
        form = OrderItemStatusForm(request.POST, instance=order_item)
        if form.is_valid():
            form.save()
            return redirect("order_detail", order_id=order.id)  # reload page

    # Add subtotal and form to each item
    total_price = 0
    for item in order_items:
        item.subtotal = item.product.price * item.quantity
        item.form = OrderItemStatusForm(instance=item)
        total_price += item.subtotal

    return render(request, "userprofile/order_detail.html", {
        "order": order,
        "order_items": order_items,
        "total_price": total_price,
    })



@login_required
def confirm_received(request, item_id):
    if request.method == "POST":
        item = get_object_or_404(OrderItem, id=item_id, order__created_by=request.user)

        # Only allow confirmation if delivered and not already received
        if item.status != 'delivered' or item.received:
            return HttpResponseForbidden("Cannot confirm this item.")

        item.confirm_received()
        return redirect('myaccount')  # Redirect back to customer dashboard






from .forms import CustomSignupForm  # use the custom form

def signup(request):
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()  # This now creates both User + Userprofile
            login(request, user)
            return redirect('frontpage')
    else:
        form = CustomSignupForm()

    return render(request, 'userprofile/signup.html', {'form': form})






def logout_view(request):
    logout(request)  # Clears the session
    return redirect('frontpage')  # Redirect to homepage


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from collections import defaultdict
from store.models import OrderItem, Products

@login_required
def completed_orders(request):
    # Fetch order items where the product belongs to this user and item is received
    order_items = OrderItem.objects.filter(
        product__user=request.user,
        status=OrderItem.STATUS_DELIVERED,
        received=True
    ).select_related('order', 'order__created_by', 'product')

    # Group items by order and calculate total price
    orders_summary = []
    orders_dict = defaultdict(list)

    for item in order_items:
        orders_dict[item.order].append(item)

    for order, items in orders_dict.items():
        total_price = sum([item.get_total_price() for item in items])
        orders_summary.append({
            'order': order,
            'items': items,
            'total_items': len(items),
            'total_price': total_price,
            'customer': order.created_by
        })

    return render(request, 'userprofile/completed_orders.html', {
        'orders_summary': orders_summary
    })

