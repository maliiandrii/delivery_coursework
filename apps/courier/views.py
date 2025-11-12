from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.orders.models import Order


@login_required
def courier_orders_view(request):
    """
    Display orders for couriers.
    Shows unassigned orders and courier's assigned orders.
    """
    if not request.user.is_courier():
        messages.error(request, 'Access denied. Couriers only.')
        return redirect('product_list')

    available_orders = Order.objects.filter(
        status='pending',
        courier__isnull=True
    )

    active_orders = Order.objects.filter(
        courier=request.user
    ).exclude(status__in=['delivered', 'cancelled'])

    finished_orders = Order.objects.filter(
        courier=request.user,
        status__in=['delivered', 'cancelled']
    )

    context = {
        'available_orders': available_orders,
        'active_orders': active_orders,
        'finished_orders': finished_orders,
    }

    return render(request, 'courier/courier_orders.html', context)


@login_required
def accept_order(request, order_id):
    """Courier accepts an order"""

    if not request.user.is_courier():
        messages.error(request, 'Access denied. Couriers only.')
        return redirect('product_list')

    order = get_object_or_404(Order, id=order_id, status='pending', courier__isnull=True)
    order.courier = request.user
    order.status = 'confirmed'
    order.save()

    messages.success(request, f'Order #{order.id} accepted successfully!')
    return redirect('courier_orders')


@login_required
def update_order_status(request, order_id):
    """Update order delivery status"""

    if not request.user.is_courier():
        messages.error(request, 'Access denied. Couriers only.')
        return redirect('product_list')

    order = get_object_or_404(Order, id=order_id, courier=request.user)

    if order.status in ['delivered', 'cancelled']:
        messages.error(request, 'Cannot update status of finished or cancelled orders')
        return redirect('courier_orders')

    if request.method == 'POST':
        new_status = request.POST.get('status')

        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order status updated to {order.get_status_display()}')
        else:
            messages.error(request, 'Invalid status')

    return redirect('courier_orders')
