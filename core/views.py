from core.models import CarouselImage
from store.models import Products
from django.db.models import F
from django.db.models.functions import Sqrt, Power
from django.shortcuts import render

from store.models import Category, Products
from django.shortcuts import get_object_or_404






def frontpage(request):
    # Base query for active products
    categories = Category.objects.all()
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

    # Annotate each queryset with average rating from reviews
    from django.db.models import Avg
    latest_products = latest_products.annotate(rating=Avg('reviews__rating'))
    sponsored_products = sponsored_products.annotate(rating=Avg('reviews__rating'))
    top_selling_products = top_selling_products.annotate(rating=Avg('reviews__rating'))
    trending_products = trending_products.annotate(rating=Avg('reviews__rating'))
    # recommended_products is empty for now, no annotation needed

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
        'categories': categories,
    }

    return render(request, 'core/frontpage.html', context)


def category_detail(request, id):
    category = get_object_or_404(Category, id=id)
    products = Products.objects.filter(category=category)

    return render(request, 'core/category_detail.html', {
        'category': category,
        'products': products,
    })


