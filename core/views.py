from core.models import CarouselImage
from store.models import Products
from django.db.models import F
from django.db.models.functions import Sqrt, Power
from django.shortcuts import render


def frontpage(request):
    # Base query for active products
    base_products = Products.objects.filter(status=Products.ACTIVE)

    # Function to annotate distance if user has location
    def annotate_distance(queryset, user):
        if user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.latitude:
            user_lat = user.userprofile.latitude
            user_lon = user.userprofile.longitude
            queryset = queryset.annotate(
                distance=Sqrt(
                    Power(F('latitude') - user_lat, 2) +
                    Power(F('longitude') - user_lon, 2)
                )
            ).order_by('distance')
        return queryset

    # Apply distance sorting to each product category
    latest_products = annotate_distance(base_products, request.user).order_by('-created_at')[:6]
    sponsored_products = annotate_distance(base_products.filter(is_sponsored=True), request.user)[:6]
    top_selling_products = annotate_distance(base_products, request.user).order_by('-sold_count')[:6]
    trending_products = annotate_distance(base_products, request.user).order_by('-views_count')[:6]

    # Recommended products placeholder (empty for now)
    recommended_products = []

    # Carousel images
    carousel_images = CarouselImage.objects.all()

    context = {
        'latest_products': latest_products,
        'sponsored_products': sponsored_products,
        'top_selling_products': top_selling_products,
        'trending_products': trending_products,
        'recommended_products': recommended_products,  # empty for now
        'carousel_images': carousel_images,
    }

    return render(request, 'core/frontpage.html', context)
