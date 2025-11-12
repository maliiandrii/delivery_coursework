from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from apps.products.models import Product
from .models import Order, OrderItem
from .forms import OrderCreateForm


@login_required
def add_to_cart(request, product_id):
    """Add product to session cart"""

    if request.user.is_courier():
        messages.error(request, 'Couriers cannot place orders')
        return redirect('courier_orders')
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin:index')

    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})

    product_id_str = str(product_id)
    if product_id_str in cart:
        cart[product_id_str]['quantity'] += 1
    else:
        cart[product_id_str] = {
            'name': product.name,
            'price': str(product.price),
            'quantity': 1,
            'image': product.image.url if product.image else None
        }

    request.session['cart'] = cart
    messages.success(request, f'{product.name} added to cart')

    return redirect(request.META.get('HTTP_REFERER', 'product_list'))


@login_required
def remove_from_cart(request, product_id):
    """Remove product from session cart"""

    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        messages.success(request, 'Item removed from cart')

    return redirect('cart_view')


@login_required
def cart_view(request):
    """Display shopping cart"""

    if request.user.is_courier():
        return redirect('courier_orders')
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin:index')

    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, item_data in cart.items():
        subtotal = float(item_data['price']) * item_data['quantity']
        cart_items.append({
            'product_id': product_id,
            'name': item_data['name'],
            'price': float(item_data['price']),
            'quantity': item_data['quantity'],
            'subtotal': round(subtotal, 2),
            'image': item_data.get('image')
        })
        total += subtotal

    total = round(total, 2)
    form = OrderCreateForm(user=request.user)

    context = {
        'cart_items': cart_items,
        'total': total,
        'form': form
    }

    return render(request, 'orders/cart.html', context)


@login_required
def create_order(request):
    """Create order from cart"""

    if request.user.is_courier():
        messages.error(request, 'Couriers cannot place orders')
        return redirect('courier_orders')
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin:index')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST, user=request.user)
        cart = request.session.get('cart', {})

        if not cart:
            messages.error(request, 'Your cart is empty')
            return redirect('product_list')

        if form.is_valid():
            order = form.save(commit=False)
            order.customer = request.user
            order.save()

            for product_id, item_data in cart.items():
                product = Product.objects.get(id=product_id)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item_data['quantity'],
                    price=item_data['price']
                )

            order.calculate_total()

            if form.cleaned_data.get('save_delivery_data'):
                request.user.address = order.delivery_address
                request.user.save()

            request.session['cart'] = {}
            messages.success(request, 'Order created successfully!')
            return redirect('order_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    return redirect('cart_view')


@login_required
def order_list_view(request):
    """Display user's orders"""

    if request.user.is_courier():
        return redirect('courier_orders')
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin:index')

    active_orders = Order.objects.filter(
        customer=request.user,
        status__in=['pending', 'confirmed', 'in_delivery']
    )

    finished_orders = Order.objects.filter(
        customer=request.user,
        status__in=['delivered', 'cancelled']
    )

    context = {
        'active_orders': active_orders,
        'finished_orders': finished_orders,
    }

    return render(request, 'orders/order_list.html', context)


@login_required
def order_detail_view(request, order_id):
    """Display order details"""

    order = get_object_or_404(Order, id=order_id)

    if request.user.is_customer():
        if order.customer != request.user:
            messages.error(request, "You don't have access to this order.")
            return redirect('order_list')

    if request.user.is_courier():
        if not (order.status == 'pending' or order.courier == request.user):
            messages.error(request, "You don't have access to this order.")
            return redirect('courier_orders')

    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin:index')

    context = {
        'order': order,
    }
    return render(request, 'orders/order_detail.html', context)


@login_required
def cancel_order(request, order_id):
    """Cancel an order if it's not delivered yet"""

    if request.user.is_courier():
        messages.error(request, 'Couriers cannot cancel orders')
        return redirect('courier_orders')
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin:index')

    order = get_object_or_404(Order, id=order_id, customer=request.user)

    if order.status in ['delivered', 'cancelled']:
        messages.error(request, 'This order cannot be cancelled')
        return redirect('order_list')

    if request.method == 'POST':
        order.status = 'cancelled'
        order.save()
        messages.success(request, f'Order #{order.id} has been cancelled')
        return redirect('order_list')

    return redirect('order_list')
