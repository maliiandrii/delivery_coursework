from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Product, Category


def product_list_view(request):
    """
    Display list of products with filtering and search.
    Redirects couriers to their dashboard.
    """
    if request.user.is_authenticated and request.user.is_courier():
        return redirect('courier_orders')

    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin:index')

    products = Product.objects.filter(available=True)
    categories = Category.objects.all()

    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    season_filter = request.GET.get('season', '')
    size_filter = request.GET.get('size', '')
    sort_by = request.GET.get('sort', '')

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if category_filter:
        products = products.filter(category__slug=category_filter)

    if season_filter:
        products = products.filter(season=season_filter)

    if size_filter:
        products = products.filter(size=size_filter)

    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')

    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'season_filter': season_filter,
        'size_filter': size_filter,
        'sort_by': sort_by,
        'season_choices': Product.SEASON_CHOICES,
        'size_choices': Product.SIZE_CHOICES,
    }

    return render(request, 'products/product_list.html', context)


def product_detail_view(request, slug):
    """Display detailed view of a single product"""

    if request.user.is_authenticated and request.user.is_courier():
        return redirect('courier_orders')
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin:index')

    product = get_object_or_404(Product, slug=slug, available=True)
    related_products = Product.objects.filter(
        category=product.category,
        available=True
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }

    return render(request, 'products/product_detail.html', context)
