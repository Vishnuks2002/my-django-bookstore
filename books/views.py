from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin 
from .models import Book, Order
from django.urls import reverse_lazy
from django.db.models import Q # for search method
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json


class BooksListView(ListView):
    model = Book
    template_name = 'list.html'
    context_object_name = 'books'


class BooksDetailView(DetailView):
    model = Book
    template_name = 'detail.html'


class SearchResultsListView(ListView):
    model = Book
    template_name = 'search_results.html'

    def get_queryset(self):  # new
        query = self.request.GET.get('q')
        return Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )


class BookCheckoutView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'checkout.html'
    login_url = 'login'


def paymentComplete(request):
    body = json.loads(request.body)
    print('BODY:', body)
    product = Book.objects.get(id=body['productId'])
    Order.objects.create(
        product=product
    )
    return JsonResponse('Payment completed!', safe=False)


def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    
    cart = request.session.get('cart')
    if not isinstance(cart, list):
        cart = []

    
    if book_id not in cart:
        cart.append(book_id)

    
    request.session['cart'] = cart

   
    referer = request.META.get('HTTP_REFERER', '/')
    return HttpResponseRedirect(referer)


def cart_view(request):
    
    cart = request.session.get('cart', [])

    
    cart_items = []
    total_cost = 0

    if isinstance(cart, list):
        cart = {str(book_id): cart.count(book_id) for book_id in cart}

    book_ids = cart.keys()
    books = Book.objects.filter(id__in=book_ids)

    
    for book in books:
        quantity = cart.get(str(book.id), 0) or cart.get(book.id, 0)
        cart_items.append({
            'book': book,
            'quantity': quantity,
            'total_price': quantity * book.price
        })

    total_cost = sum(item['total_price'] for item in cart_items)

    
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_cost': total_cost
    })


@require_POST
def remove_from_cart(request, book_id):
    cart = request.session.get('cart', [])

    if isinstance(cart, list):
        cart = [int(id) for id in cart if int(id) != book_id]

    request.session['cart'] = cart
    return redirect('cart')
