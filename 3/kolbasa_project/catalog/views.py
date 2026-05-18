from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Kolbasa, Kind, Cart, CartItem
from .forms import KolbasaForm, CartDiscountForm, CartItemForm
from django.contrib.auth.decorators import login_required, permission_required


def product_list(request):
    sort = request.GET.get('sort', 'brand')
    dir = request.GET.get('dir', 'asc')
    valid_sort_fields = {
        'brand': 'brand',
        'weight': 'weight',
        'kind': 'kind__name',
        'num_slices': 'num_of_slices',
    }
    order_field = valid_sort_fields.get(sort, 'brand')
    if dir == 'desc':
        order_field = f'-{order_field}'

    queryset = Kolbasa.objects.all().order_by(order_field)

    # Поиск и фильтрация (как раньше)
    search_query = request.GET.get('q', '')
    if search_query:
        queryset = queryset.filter(
            Q(brand__icontains=search_query) | Q(kind__name__icontains=search_query)
        )

    kind_filter = request.GET.get('kind', '')
    if kind_filter:
        queryset = queryset.filter(kind_id=kind_filter)

    precut_filter = request.GET.get('precut', '')
    if precut_filter == 'yes':
        queryset = queryset.filter(precut=True)
    elif precut_filter == 'no':
        queryset = queryset.filter(precut=False)

    kinds = Kind.objects.all()

    context = {
        'title': 'Каталог колбас',
        'kolbasas': queryset,
        'search_query': search_query,
        'kinds': kinds,
        'selected_kind': kind_filter,
        'selected_precut': precut_filter,
        'current_sort': sort,
    }
    context['current_sort'] = sort
    context['current_dir'] = dir
    return render(request, 'catalog/product_list.html', context)


def kind_groups(request):
    """Страница с группами товаров по типу (полю «один из»)."""
    kinds = Kind.objects.prefetch_related('kolbasas').all()
    context = {
        'title': 'Группы колбас по типу',
        'kinds': kinds,
    }
    return render(request, 'catalog/kind_groups.html', context)


def product_detail(request, pk):
    """Детальная страница товара."""
    kolbasa = get_object_or_404(Kolbasa, pk=pk)
    try:
        weight_per_slice = kolbasa.weight_per_slice if kolbasa.precut else None
    except ValueError as e:
        weight_per_slice = None
        error_msg = str(e)
    else:
        error_msg = None

    context = {
        'title': f'Колбаса {kolbasa.brand}',
        'kolbasa': kolbasa,
        'weight_per_slice': weight_per_slice,
        'error_msg': error_msg,
    }
    return render(request, 'catalog/product_detail.html', context)


@login_required
@permission_required('catalog.add_kolbasa', raise_exception=True)
def product_create(request):
    """Добавление нового товара."""
    if request.method == 'POST':
        form = KolbasaForm(request.POST)
        if form.is_valid():
            kolbasa = form.save()
            messages.success(request, f'Колбаса "{kolbasa.brand}" успешно добавлена!')
            return redirect('product_detail', pk=kolbasa.pk)
    else:
        form = KolbasaForm()
    return render(request, 'catalog/product_form.html', {
        'form': form,
        'title': 'Добавить колбасу',
        'submit_text': 'Добавить'
    })


@login_required
@permission_required('catalog.add_kolbasa', raise_exception=True)
def product_edit(request, pk):
    """Редактирование товара."""
    kolbasa = get_object_or_404(Kolbasa, pk=pk)
    if request.method == 'POST':
        form = KolbasaForm(request.POST, instance=kolbasa)
        if form.is_valid():
            kolbasa = form.save()
            messages.success(request, f'Колбаса "{kolbasa.brand}" обновлена!')
            return redirect('product_detail', pk=kolbasa.pk)
    else:
        form = KolbasaForm(instance=kolbasa)
    return render(request, 'catalog/product_form.html', {
        'form': form,
        'title': f'Редактировать: {kolbasa.brand}',
        'submit_text': 'Сохранить'
    })


@login_required
@permission_required('catalog.add_kolbasa', raise_exception=True)
def product_delete(request, pk):
    """Удаление товара."""
    kolbasa = get_object_or_404(Kolbasa, pk=pk)
    if request.method == 'POST':
        brand = kolbasa.brand
        kolbasa.delete()
        messages.success(request, f'Колбаса "{brand}" удалена.')
        return redirect('product_list')
    return render(request, 'catalog/product_confirm_delete.html', {
        'kolbasa': kolbasa,
        'title': f'Удалить {kolbasa.brand}?'
    })


def about(request):
    """О сервисе."""
    return render(request, 'catalog/about.html', {'title': 'О нашем сервисе'})


@login_required
@permission_required('catalog.add_cart', raise_exception=True)
def cart_detail(request):
    cart, _ = Cart.objects.get_or_create(user=request.user, status='draft')
    if request.method == 'POST':
        form = CartDiscountForm(request.POST, instance=cart)
        if form.is_valid():
            form.save()
            messages.success(request, 'Скидка обновлена.')
            return redirect('cart_detail')
    else:
        form = CartDiscountForm(instance=cart)
    items = cart.items.select_related('product').all()
    return render(request, 'catalog/cart_detail.html', {'cart': cart, 'items': items, 'form': form})


@login_required
@permission_required('catalog.add_cart', raise_exception=True)
def add_to_cart(request, product_pk):
    product = get_object_or_404(Kolbasa, pk=product_pk)
    cart, _ = Cart.objects.get_or_create(user=request.user, status='draft')
    if request.method == 'POST':
        # Создаём экземпляр, но не сохраняем, чтобы передать cart и product
        item = CartItem(cart=cart, product=product)
        form = CartItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()  # здесь сработает переопределённый save() и установит цену
            messages.success(request, f'{product.brand} добавлен в корзину.')
            return redirect('cart_detail')
    else:
        form = CartItemForm()
    return render(request, 'catalog/add_to_cart.html', {'form': form, 'product': product})

@login_required
@permission_required('catalog.add_cart', raise_exception=True)
def remove_from_cart(request, item_pk):
    item = get_object_or_404(CartItem, pk=item_pk, cart__user=request.user, cart__status='draft')
    item.delete()
    return redirect('cart_detail')

@login_required
@permission_required('catalog.add_cart', raise_exception=True)
def submit_cart(request):
    cart = get_object_or_404(Cart, user=request.user, status='draft')
    if request.method == 'POST':
        cart.status = 'submitted'
        cart.save()
        messages.success(request, 'Корзина отправлена.')
        return redirect('cart_list')
    return render(request, 'catalog/confirm_submit.html', {'cart': cart})

def cart_list(request):
    if request.user.is_authenticated and request.user.has_perm('catalog.add_cart'):
        carts = Cart.objects.filter(user=request.user, status='submitted')
    else:
        carts = []
    return render(request, 'catalog/cart_list.html', {'carts': carts})
