from django.core.management.base import BaseCommand
from store.models import Products, OrderItem, ProductView
from core.redis_client import redis_client
from django.contrib.auth.models import User
from collections import Counter

class Command(BaseCommand):
    help = "Precompute product recommendations for all users"

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        for user in users:
            # Step 1: Get products user already bought
            bought_products = OrderItem.objects.filter(order__created_by=user)\
                                .values_list('product', flat=True)

            # Step 2: Collaborative Filtering
            # Find other users who bought same products
            other_user_ids = OrderItem.objects.filter(product__in=bought_products)\
                                .exclude(order__created_by=user)\
                                .values_list('order__created_by', flat=True)

            # Products those users bought excluding what current user already has
            recommended_products = OrderItem.objects.filter(order__created_by__in=other_user_ids)\
                                    .exclude(product__in=bought_products)\
                                    .values_list('product', flat=True)

            # Step 3: Add content-based recommendations
            categories = Products.objects.filter(id__in=bought_products)\
                                .values_list('category', flat=True)
            content_based_products = Products.objects.filter(category__in=categories)\
                                        .exclude(id__in=bought_products)\
                                        .values_list('id', flat=True)

            # Merge both lists and count frequency
            combined = list(recommended_products) + list(content_based_products)
            counter = Counter(combined)
            top_products = [pid for pid, _ in counter.most_common(10)]  # top 10

            # Step 4: Save to Redis
            redis_key = f"user:{user.id}:recommendations"
            redis_client.delete(redis_key)
            if top_products:
                redis_client.rpush(redis_key, *top_products)

        self.stdout.write(self.style.SUCCESS('Recommendations precomputed for all users.'))
