from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from .models import Userprofile
from store.forms import ProductForm, StoreForm, OrderItemStatusForm
from store.models import Products, Category, OrderItem, Order
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

@login_required
def mystore(request):
    # Products for this vendor
    products = request.user.products.exclude(status=Products.DELETED)
    
    # All order items for this vendor
    order_items = OrderItem.objects.filter(
        product__user=request.user
    ).select_related('order', 'order__created_by', 'product')

    # Group items by order
    orders_dict = defaultdict(list)
    for item in order_items:
        orders_dict[item.order].append(item)

    underway_orders = []
    history_orders = []

    # Build summaries
    for order, items in orders_dict.items():
        total_price = sum([item.get_total_price() for item in items])
        order_summary = {
            'order': order,
            'items': items,
            'total_items': len(items),
            'total_price': total_price,
            'customer': order.created_by,
            'completed': all(
                (item.status == OrderItem.STATUS_DELIVERED and item.received is True)
                for item in items
            )


        }

        # Split orders
        if order_summary['completed']:
            history_orders.append(order_summary)
        else:
            underway_orders.append(order_summary)

    context = {
        'products': products,
        'underway_orders': underway_orders,
        'history_orders': history_orders,
    }

    return render(request, 'userprofile/mystore.html', context)


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

