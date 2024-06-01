from django.db import models
from django.contrib.auth.models import User

class CartQuery(models.QuerySet):

    def total_items(self):
        if self:
            return sum(cart.quantity for cart in self)
        return 0
    
    def total_price(self):
        return sum(cart.total_item_price() for cart in self)

class Categories(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name='Name')
    category_slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name='URL')

    class Meta:
        db_table = 'Category'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Item(models.Model):
    title = models.CharField(max_length = 100, blank = False)
    price = models.DecimalField(blank = False, null = False, decimal_places=2, max_digits=8)
    description = models.CharField(max_length = 200, blank = False)
    quantity = models.IntegerField(blank = False)
    image = models.ImageField(blank = True, null = True)
    rating = models.FloatField(blank = True)
    sale = models.DecimalField(default=0.00, max_digits=4, decimal_places=2)
    category = models.ForeignKey(to=Categories, on_delete=models.CASCADE, verbose_name='Категория')
    slug = models.SlugField(max_length = 200, unique = True, blank = True, null = True, verbose_name = 'Item_URL')

    class Meta:
        db_table = 'Items'
        verbose_name = 'Item'
        verbose_name_plural = 'Items'

    def __str__(self):
        return self.title
    
    @property
    def image_url(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    
    def sell_price(self):
        if self.sale:
            return round(self.price - self.price*self.sale / 100, 2) 
        return self.price
        

class Cart(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    contents = models.ForeignKey(to=Item, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=0)
    session_key = models.CharField(max_length=35, null=True, blank=True)

    def __str__(self):
        if self.user:
            return f"Cart: {self.user} / Contents: {self.contents.title} / Quantity: {self.quantity}"
        return f"Anonymous / Contents: {self.contents.title} / Quantity: {self.quantity}"
    
    def total_item_price(self):
        return round(self.contents.sell_price() * self.quantity, 2)
    
    objects = CartQuery().as_manager()
