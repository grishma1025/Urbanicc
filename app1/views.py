from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import ContactForm, ReviewForm
import razorpay
from django.http import JsonResponse
from django.db.models import Sum
from collections import Counter
from django.db.models import F, Sum


# ------------------ STATIC PAGES ------------------

def index(request):
    return render(request, 'index.html')

def about_us(request):
    return render(request, 'about_us.html')

def blog_details(request):
    return render(request, 'blog_details.html')

def blog(request):
    return render(request, 'blog.html')

def main(request):
    return render(request, 'main.html')


# ------------------ PRODUCT DETAILS ------------------

def product_details(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.exclude(id=product.id)[:4]

    images = product.images.all()
    variants = product.variants.all()

    review_form = ReviewForm()

    if request.method == "POST" and request.POST.get('action') == 'add_review':
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.approved = True
            review.save()

            product.update_rating()

            messages.success(request, "Your review was submitted successfully.")
            return redirect('product_details', slug=product.slug)
        else:
            messages.error(request, "There was an issue submitting your review.")

    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    return render(request, 'product_details.html', {
        'product': product,
        'related_products': related_products,
        'images': images,
        'variants': variants,
        'review_form': review_form,
        'in_wishlist': in_wishlist,
    })


# ------------------ SHOP PAGE ------------------

def shop(request):
    product_list = Product.objects.all().order_by('-created_at')
    paginator = Paginator(product_list, 9)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    return render(request, "shop.html", {"products": products})


# ------------------ USER AUTH ------------------

def register(request):
    if request.method == "POST":
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        uname = request.POST['uname']
        pwd = request.POST['pwd']
        cpwd = request.POST['cpwd']

        if pwd != cpwd:
            messages.error(request, "Passwords do not match!")
            return redirect('/register/')

        if User.objects.filter(username=uname).exists():
            messages.error(request, "Username already exists!")
            return redirect('/register/')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('/register/')

        user = User.objects.create_user(
            first_name=fname,
            last_name=lname,
            email=email,
            username=uname,
            password=pwd
        )
        user.save()

        messages.success(request, "Registration successful! Please login.")
        return redirect('/login/')

    return render(request, 'register.html')


def login(request):
    if request.method == "POST":
        un = request.POST['uname']
        p1 = request.POST['pwd']

        user = auth.authenticate(username=un, password=p1)

        if user:
            auth.login(request, user)
            messages.success(request, f"Welcome {user.username}!")
            return redirect('/')
        else:
            messages.error(request, "Invalid username or password!")
            return redirect('/login/')

    return render(request, 'login.html')


def logout(request):
    auth.logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('/')


# ------------------ CONTACT FORM ------------------

def contact_view(request):
    if request.method == 'POST':
        Contact.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            message=request.POST.get('message')
        )

        return render(request, 'contact.html', {'success': True})

    return render(request, 'contact.html')


# ------------------ CART (DB BASED ONLY) ------------------

@login_required(login_url='/login/')
def shop_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    subtotal = sum(item.subtotal for item in cart_items)

    return render(request, 'shop_cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': subtotal,
    })


@login_required(login_url='/login/')
def remove_from_cart(request, id):
    item = get_object_or_404(Cart, id=id)
    item.delete()
    messages.success(request, "Item removed from cart!")
    return redirect('shop_cart')


# ------------------ ADD TO CART ------------------

@login_required(login_url='/login/')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )
    cart_item.quantity += 1
    cart_item.save()

    messages.success(request, "Product added to cart")
    return redirect("shop_cart")


# ------------------ WISHLIST ------------------

@login_required(login_url='/login/')
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if not created:
        item.delete()
        messages.info(request, "Removed from wishlist.")
    else:
        messages.success(request, "Added to wishlist!")

    return redirect('product_details', slug=product.slug)


@login_required(login_url='/login/')
def wishlist_page(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, "wishlist.html", {"wishlist_items": wishlist_items})


@login_required(login_url='/login/')
def move_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    Wishlist.objects.filter(user=request.user, product=product).delete()

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )
    cart_item.quantity += 1
    cart_item.save()

    messages.success(request, f"{product.title} moved to cart.")
    return redirect("shop_cart")


# ------------------ BLOG ------------------

def blog_list(request):
    posts = Blog.objects.all().order_by('-created_at')
    return render(request, 'blog.html', {'posts': posts})

def blog_detail(request, slug):
    post = Blog.objects.get(slug=slug)
    return render(request, 'blog_details.html', {'post': post})


# ------------------ CHECKOUT ------------------

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_amount = sum(item.subtotal for item in cart_items)

    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "total_amount": total_amount,
    })


# ------------------ PLACE ORDER + RAZORPAY ------------------
# ------------------ PLACE ORDER (NO PAYMENT) ------------------

@login_required
def place_order(request):
    if request.method == "POST":
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect("shop_cart")

        # calculate total
        total_amount = sum(item.subtotal for item in cart_items)

        # create order
        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
            payment_method="COD",
            payment_status="PENDING"
        )

        # create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # clear cart
        cart_items.delete()

        messages.success(request, "Order placed successfully!")
        return redirect("order_success")

    return redirect("checkout")


@login_required(login_url='/login/')
def update_cart(request, cart_id):
    if request.method == "POST":
        cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
        qty = int(request.POST.get("quantity", 1))

        if qty < 1:
            qty = 1

        cart_item.quantity = qty
        cart_item.save()

        messages.success(request, "Cart updated successfully!")

    return redirect("shop_cart")

@login_required
def order_success(request):
    return render(request, "checkout.html")


# ------------------ reports ------------------


@login_required
def reports(request):
    return render(request, 'reports.html')



# 📊 Product stock
def product_chart_data(request):
    products = Product.objects.all()

    labels = [p.title for p in products]
    values = [p.stock for p in products]

    return JsonResponse({
        'labels': labels,
        'values': values
    })


# 📈 Orders over time
def order_chart_data(request):
    orders = Order.objects.all().order_by('created_at')

    labels = [o.created_at.strftime("%Y-%m-%d") for o in orders]
    values = [o.total_amount for o in orders]

    return JsonResponse({
        'labels': labels,
        'values': values
    })


# 🥧 Top products sold

def top_products_data(request):
    items = OrderItem.objects.values('product__title')\
        .annotate(total_sold=Sum('quantity'))\
        .order_by('-total_sold')[:5]

    total = sum(item['total_sold'] for item in items) or 1  # avoid divide by 0

    labels = [item['product__title'] for item in items]
    values = [round((item['total_sold'] / total) * 100, 2) for item in items]

    return JsonResponse({
        'labels': labels,
        'values': values
    })


# 📊 Revenue per product
def revenue_per_product(request):
    items = OrderItem.objects.values('product__title')\
        .annotate(total_revenue=Sum(F('price') * F('quantity')))\
        .order_by('-total_revenue')

    total = sum(item['total_revenue'] for item in items) or 1

    labels = [item['product__title'] for item in items]
    values = [round((item['total_revenue'] / total) * 100, 2) for item in items]

    return JsonResponse({
        'labels': labels,
        'values': values
    })