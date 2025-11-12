def cart_count(request):
    """Add cart item count to all templates"""
    cart = request.session.get('cart', {})
    total_items = sum(item['quantity'] for item in cart.values())
    return {'cart_count': total_items}
