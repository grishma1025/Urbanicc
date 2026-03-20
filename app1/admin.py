from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse

from .models import Contact, Product, ProductImage, ProductVariant, Review, Wishlist, Blog, Order, OrderItem


# ------------------ CUSTOM ADMIN DASHBOARD ------------------

class CustomAdminSite(admin.AdminSite):
    site_header = "My Admin Panel"
    site_title = "Admin Dashboard"
    index_title = "Welcome to Admin Panel"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard))
        ]
        return custom_urls + urls

    def dashboard(self, request):
        context = dict(
            self.each_context(request),
        )
        return TemplateResponse(request, "admin/dashboard.html", context)


custom_admin_site = CustomAdminSite(name='custom_admin')


# ------------------ INLINE CLASSES ------------------

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ('user_name', 'rating', 'body', 'created_at')
    can_delete = True


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


# ------------------ MODEL ADMINS ------------------

@admin.register(Product, site=custom_admin_site)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'sale', 'stock', 'created_at', 'slug')
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProductImageInline, ProductVariantInline, ReviewInline]
    search_fields = ('title',)


@admin.register(Order, site=custom_admin_site)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_amount", "payment_method", "payment_status", "created_at")
    inlines = [OrderItemInline]


# ------------------ REGISTER OTHER MODELS ------------------

custom_admin_site.register(Contact)
custom_admin_site.register(ProductImage)
custom_admin_site.register(ProductVariant)
custom_admin_site.register(Review)
custom_admin_site.register(Wishlist)
custom_admin_site.register(Blog)
custom_admin_site.register(OrderItem)