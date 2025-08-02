from django.db import models
from users.models import User
from market.models import Item
from django.db.models import Count


class ReviewManager(models.Manager):
    def reviews_percentage(self, item_slug):
        qset = super().get_queryset().filter(item__slug=item_slug)
        data = qset.values('rating').annotate(count=Count('id'),
                                            percentage=models.functions.Cast(100.0*Count('id') / qset.count(),
                                            output_field=models.FloatField())).order_by('-rating')
        
        result = {}
        formatted = {item['rating']: item['percentage'] for item in data}

        for num in range(1, 6):
            result[str(num)] = round(formatted.get(num, 0.00))

        return result

class Review(models.Model):
    author = models.ForeignKey(to=User, null=False, blank=False, on_delete=models.CASCADE)
    item = models.ForeignKey(to=Item, null=False, blank=False, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    title = models.CharField(null=False, blank=False, max_length=50)
    text = models.CharField(null=True, blank=False, max_length=200)
    created_at = models.TimeField(auto_now_add=True)

    objects = ReviewManager()

    class Meta:
        db_table = 'reviews'