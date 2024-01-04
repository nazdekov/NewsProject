from django.shortcuts import render, HttpResponse, HttpResponseRedirect, redirect
from .models import *
from .forms import *

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group

def profile(request):
    context = dict()
    return render(request, 'users/profile.html', context)

from .forms import AccountUpdateForm, UserUpdateForm
from django.contrib.auth.decorators import login_required
from news.models import Article

@login_required
def add_to_favorites(request, id):
    article = Article.objects.get(id=id)
    #проверям есть ли такая закладка с этой новостью
    bookmark = FavoriteArticle.objects.filter(user=request.user.id, article=article)
    if bookmark.exists():
        bookmark.delete()
        messages.warning(request, f"Новость {article.title} удалена из закладок")
    else:
        bookmark = FavoriteArticle.objects.create(user=request.user, article=article)
        messages.success(request, f"Новость {article.title} добавлена в закладки")
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def profile_update(request):
    user = request.user
    account = Account.objects.get(user=user)
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=user)
        account_form = AccountUpdateForm(request.POST, request.FILES, instance=account)
        if user_form.is_valid() and account_form.is_valid():
            user_form.save()
            account_form.save()
            messages.success(request, "Профиль успешно обновлен")
            return redirect('profile')
        else:
            print('!!!!!!!!!, Если формы не валидны')
            pass
    else:
        context = {'account_form': AccountUpdateForm(instance=account),
                   'user_form': UserUpdateForm(instance=user)}
    return render(request, 'users/edit_profile.html', context)


@login_required
def profile_delete(request):
    user = request.user
    user.delete()
    return redirect('news_index')
@login_required
def delete_akk(request):
    return render(request, 'users/delete_profile.html')


from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
def password_update(request):
    user = request.user
    form = PasswordChangeForm(user, request.POST)
    if request.method == 'POST':
        if form.is_valid():
            password_info = form.save()
            update_session_auth_hash(request, password_info)
            messages.success(request, 'Пароль успешно изменен')
            return redirect('profile')

    context = {"form": form}
    return render(request, 'users/edit_password.html', context)


def registration(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save() #появляется новый пользователь
            category = request.POST['account_type']
            if category == 'author':
                group = Group.objects.get(name='Actions Required')
                user.groups.add(group)
            else:
                group = Group.objects.get(name='Readers')
                user.groups.add(group)
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            account = Account.objects.create(user=user, nickname=user.username)
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, f'{username} был зарегистрирован!')

            return redirect('home')
    else:
        form = UserCreationForm()
    context = {'form': form}
    return render(request, 'users/registration.html', context)


def contact_page(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            print('Сообщение отправлено', form.cleaned_data)
        else:
            print('Ошибка', form.errors)
    else:
        form = ContactForm()
    context = {'form': form}
    return render(request, 'users/contact_page.html', context)


def index(request):
    print(request.user, request.user.id)
    try:
        user_acc = Account.objects.get(user=request.user)
        print(user_acc.birthdate, user_acc.gender)
        return HttpResponse(f"Приложение Users, {request.user} | {request.user.id} | {user_acc.nickname}, {request.GET}")
    except:
        return HttpResponse('Не авторизован')


from django.core.paginator import Paginator
def my_news_list(request):
    categories = Article.categories #создали перечень категорий
    author = User.objects.get(id=request.user.id) #фильтр по автору
    articles = Article.objects.filter(author=author)
    if request.method == "POST":
        selected_category = int(request.POST.get('category_filter'))
        if selected_category != 0: #фильтруем найденные результаты по категориям
            articles = articles.filter(category__icontains=categories[selected_category-1][0])
    else: #если страница открывется впервые
        selected_category = 0

    articles = articles.order_by('-date')
    total = len(articles)
    p = Paginator(articles, 6)
    page_number = request.GET.get('page')
    page_obj = p.get_page(page_number)
    context = {'articles': page_obj, 'total': total,
               'categories': categories, 'selected_category': selected_category}

    return render(request, 'users/my_news_list.html', context)

def my_favorites_list(request):
    articles = Article.objects.filter(favoritearticle__user=request.user)
    categories = Article.categories #создали перечень категорий
    author_list = User.objects.filter(article__isnull=False).filter(article__status=True).filter(favoritearticle__isnull=False).distinct() #создали перечень авторов

    selected_author = request.session.get('author_filter')
    selected_category = request.session.get('category_filter')
    selected_author = 0 if selected_author == None else selected_author
    selected_category = 0 if selected_category == None else selected_category

    if request.method == "POST": #при обработке POST - мы только сохраняяем в сессию выбранных авторов
        selected_author = int(request.POST.get('author_filter'))
        selected_category = int(request.POST.get('category_filter'))
        request.session['author_filter'] = selected_author
        request.session['category_filter'] = selected_category
        return redirect('my_favorites_list')
    else: #если страница открывется впервые или нас переадресовала сюда функция поиск
        if selected_author != 0:  # если не пустое - находим нужные новости
            articles = articles.filter(author=selected_author)
        if selected_category != 0:  # фильтруем найденные по авторам результаты по категориям
            articles = articles.filter(category__icontains=categories[selected_category - 1][0])

    articles = articles.order_by('-date')
    total = len(articles)
    p = Paginator(articles, 6)
    page_number = request.GET.get('page')
    page_obj = p.get_page(page_number)
    context = {'articles': page_obj, 'author_list': author_list, 'selected_author': selected_author,
               'categories': categories, 'selected_category': selected_category, 'total': total}

    return render(request, 'users/my_favorites_list.html', context)