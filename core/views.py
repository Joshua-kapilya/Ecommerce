from core.redis_client import redis_client
from django.shortcuts import render
from store.models import Products
from core.models import CarouselImage  # Import carousel model

def frontpage(request):
    # Products
    latest_products = Products.objects.filter(status=Products.ACTIVE).order_by('-created_at')[:6]
    sponsored_products = Products.objects.filter(status=Products.ACTIVE, is_sponsored=True)[:6]
    top_selling_products = Products.objects.filter(status=Products.ACTIVE).order_by('-sold_count')[:6]
    trending_products = Products.objects.filter(status=Products.ACTIVE).order_by('-views_count')[:6]

    # Recommended products
    recommended_products = []
    if request.user.is_authenticated:
        product_ids = redis_client.lrange(f"user:{request.user.id}:recommendations", 0, 9)
        if product_ids:
            recommended_products = Products.objects.filter(id__in=product_ids)

    # Carousel images
    carousel_images = CarouselImage.objects.all()

    context = {
        'latest_products': latest_products,
        'sponsored_products': sponsored_products,
        'top_selling_products': top_selling_products,
        'trending_products': trending_products,
        'recommended_products': recommended_products,
        'carousel_images': carousel_images,  # Added carousel to context
    }

    return render(request, 'core/frontpage.html', context)
