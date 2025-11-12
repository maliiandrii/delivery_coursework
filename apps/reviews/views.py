from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.orders.models import Order
from .models import Review
from .forms import ReviewForm


def review_list_view(request):
    """Display all reviews"""

    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin:index')

    reviews = Review.objects.all()

    context = {
        'reviews': reviews,
    }

    return render(request, 'reviews/review_list.html', context)


@login_required
def create_review(request, order_id):
    """Create a review for a completed order"""

    order = get_object_or_404(Order, id=order_id, customer=request.user)

    if not order.is_finished():
        messages.error(request, 'You can only review completed orders')
        return redirect('order_list')

    if hasattr(order, 'review'):
        messages.error(request, 'You have already reviewed this order')
        return redirect('order_list')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.order = order
            review.user = request.user
            review.save()
            messages.success(request, 'Review submitted successfully!')
            return redirect('order_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    return redirect('order_list')
