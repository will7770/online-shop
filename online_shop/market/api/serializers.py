from rest_framework import serializers



class CartAddSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(write_only=True)
    message = serializers.CharField(read_only=True)
    cart_items_html = serializers.CharField(read_only=True)
    
    
class CartChangeSerializer(serializers.Serializer):
    cart_id = serializers.IntegerField(write_only=True)
    quantity = serializers.IntegerField(write_only=True)
    cart_items_html = serializers.CharField(read_only=True)


class CartDeleteSerializer(serializers.Serializer):
    cart_id = serializers.IntegerField(write_only=True)
    message = serializers.CharField(read_only=True)
    cart_items_html = serializers.CharField(read_only=True)