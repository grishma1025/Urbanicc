from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('blog_details/', blog_details, name='blog_details'),
    path('blog/', blog_list, name='blog'),
    path('checkout/', checkout, name='checkout'),
    path('main/', main, name='main'),

    # Product details
    path('product/<slug:slug>/', product_details, name='product_details'),

    # Cart (DB-based)
    path('shop_cart/', shop_cart, name='shop_cart'),
    path("add-to-cart/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path("move-to-cart/<int:product_id>/", move_to_cart, name="move_to_cart"),
    path("remove-from-cart/<int:id>/", remove_from_cart, name="remove_from_cart"),

    # FIXED update_cart (uses cart_id)
    path("update-cart/<int:cart_id>/", update_cart, name="update_cart"),

    # Place Order
    path("place-order/", place_order, name="place_order"),
path("order-success/", order_success, name="order_success"),


    # Shop
    path('shop/', shop, name='shop'),

    # Auth
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),

    # Contact
    path('contact/', contact_view, name='contact'),

    # Wishlist
    path("wishlist/", wishlist_page, name="wishlist_page"),
    path("wishlist/toggle/<int:product_id>/", toggle_wishlist, name="toggle_wishlist"),

    # About
    path('about_us/', about_us, name='about_us'),

    # Blog Details
    path('blog/<slug:slug>/', blog_detail, name='blog_detail'),

    #reports
    path('reports/', reports, name='reports'),
    path('product-data/', product_chart_data),
path('order-data/', order_chart_data),
path('top-products/', top_products_data),
path('revenue-products/', revenue_per_product),
]
