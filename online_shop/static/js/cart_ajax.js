// When HTML document is ready
$(document).ready(function () {
    // DOM elements
    var successMessage = $("#jq-notification");
    var notification = $('#notification');
    var cartModal = new bootstrap.Modal(document.getElementById('cartModal'));

    // Notification handling
    if (notification.length > 0) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(notification[0]);
            bsAlert.close();
        }, 4000);
    }

    // Modal handling
    $('#cartModalButton').click(function() {
        cartModal.show();
    });
    
    $('#cartModal .btn-close').click(function() {
        cartModal.hide();
    });

    // Cart functions
    function updateCart(cartID, quantity, change, url) {
        $.ajax({
            type: "POST",
            url: url,
            data: {
                cart_id: cartID,
                quantity: quantity,
                csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
            },
            success: function (data) {
                successMessage.html(data.message);
                successMessage.fadeIn(400);
                setTimeout(function () {
                    successMessage.fadeOut(400);
                }, 4000);

                var goodsInCartCount = $("#goods-in-cart-count");
                var cartCount = parseInt(goodsInCartCount.text() || 0);
                cartCount += change;
                goodsInCartCount.text(cartCount);

                var cartItemsContainer = $("#cart-items-container");
                cartItemsContainer.html(data.cart_items_html);
            },
            error: function (data) {
                console.log("Error updating product quantity");
            },
        });
    }

    // Event handlers
    $(document)
        // Add to cart
        .on("click", ".add-to-cart", function (e) {
            e.preventDefault();

            var goodsInCartCount = $("#goods-in-cart-count");
            var cartCount = parseInt(goodsInCartCount.text() || 0);
            var product_id = $(this).data("product-id");
            var add_to_cart_url = $(this).attr("href");

            $.ajax({
                type: "POST",
                url: add_to_cart_url,
                data: {
                    product_id: product_id,
                    csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
                },
                success: function (data) {
                    successMessage.html(data.message);
                    successMessage.fadeIn(400);
                    setTimeout(function () {
                        successMessage.fadeOut(400);
                    }, 4000);

                    cartCount++;
                    goodsInCartCount.text(cartCount);

                    var cartItemsContainer = $("#cart-items-container");
                    cartItemsContainer.html(data.cart_items_html);
                },
                error: function (data) {
                    console.log("Error adding product to cart");
                },
            });
        })
        
        // Remove from cart
        .on("click", ".remove-from-cart", function (e) {
            e.preventDefault();

            var goodsInCartCount = $("#goods-in-cart-count");
            var cartCount = parseInt(goodsInCartCount.text() || 0);
            var cart_id = $(this).data("cart-id");
            var remove_from_cart = $(this).attr("href");

            $.ajax({
                type: "POST",
                url: remove_from_cart,
                data: {
                    cart_id: cart_id,
                    csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
                },
                success: function (data) {
                    successMessage.html(data.message);
                    successMessage.fadeIn(400);
                    setTimeout(function () {
                        successMessage.fadeOut(400);
                    }, 4000);

                    cartCount -= data.quantity_deleted;
                    goodsInCartCount.text(cartCount);

                    var cartItemsContainer = $("#cart-items-container");
                    cartItemsContainer.html(data.cart_items_html);
                },
                error: function (data) {
                    console.log("Error removing product from cart");
                },
            });
        })
        
        // Quantity decrement
        .on("click", ".decrement", function () {
            var url = $(this).data("cart-change-url");
            var cartID = $(this).data("cart-id");
            var $input = $(this).closest('.input-group').find('.number');
            var currentValue = parseInt($input.val());
            
            if (currentValue > 1) {
                $input.val(currentValue - 1);
                updateCart(cartID, currentValue - 1, -1, url);
            }
        })
        
        // Quantity increment
        .on("click", ".increment", function () {
            var url = $(this).data("cart-change-url");
            var cartID = $(this).data("cart-id");
            var $input = $(this).closest('.input-group').find('.number');
            var currentValue = parseInt($input.val());

            $input.val(currentValue + 1);
            updateCart(cartID, currentValue + 1, 1, url);
        });
});