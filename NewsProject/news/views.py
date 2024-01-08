from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse_lazy
from .models import *
from .forms import *
from users.utils import * #импортировли декоратор
from django.views.generic import DetailView, DeleteView, UpdateView
from django.contrib.auth.decorators import login_required
#человек не аутентифицирован - отправляем на страницу другую

import json

def search_auto(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        q = request.GET.get('term', '')
        articles = Article.objects.filter(title__icontains=q)
        results = []
        for a in articles:
            results.append(a.title)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

def search(request):
    if request.method == 'POST': #пришел запрос из меню поиска
        value = request.POST['search_input'] #находим новости
        request.session['search_input'] = value
        return redirect('news_index')
    else:
        return redirect('home')


def get_bookmark_user(request):
    user = request.user.id
    print('!!!!!!!!, user: ', user)
    return user


from users.models import FavoriteArticle
from .utils import ViewCountMixin
class ArticleDetailView(ViewCountMixin, DetailView):
    model = Article
    template_name = 'news/news_detail.html'
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_object = self.object

        # формируем QS-list с id пользователей
        us = FavoriteArticle.objects.filter(article=current_object.pk).select_related('user').values_list('user__id', flat=True)
        context['users'] = us

        #проверям есть ли такая закладка с этой новостью
        bookmark = FavoriteArticle.objects.filter(article=current_object.pk)
        context['bookmark'] = bookmark.exists()

        images = Image.objects.filter(article=current_object)
        context['images'] = images

        return context


class ArticleUpdateView(UpdateView):
    model = Article
    template_name = 'news/create_article.html'
    fields = ['title', 'anouncement', 'text', 'tags']

    def get_context_data(self, **kwargs):
        context = super(ArticleUpdateView, self).get_context_data(**kwargs)
        current_object = self.object
        images = Image.objects.filter(article=current_object)
        context['image_form'] = ImagesFormSet(instance=current_object)
        return context
    def post(self, request, **kwargs):
        current_object = Article.objects.get(id=request.POST['image_set-0-article'])
        deleted_ids = []
        for i in range(int(request.POST['image_set-TOTAL_FORMS'])): #удаление всем по галочкам
            field_delete = f'image_set-{i}-DELETE'
            field_image_id = f'image_set-{i}-id'
            if field_delete in request.POST and request.POST[field_delete] == 'on':
                image = Image.objects.get(id=request.POST[field_image_id])
                image.delete()
                deleted_ids.append(field_image_id)

                #тут же удалить картинку из request.FILES
        #Замена картинки
        for i in range(int(request.POST['image_set-TOTAL_FORMS'])):  # удаление всех по галочкам
            field_replace = f'image_set-{i}-image' #должен быть в request.FILES
            field_image_id = f'image_set-{i}-id'  #этот файл мы заменим
            if field_replace in request.FILES and request.POST[field_image_id] != '' and field_image_id not in deleted_ids:
                image = Image.objects.get(id=request.POST[field_image_id]) #
                image.delete() #удаляем старый файл
                for img in request.FILES.getlist(field_replace): #новый добавили
                    Image.objects.create(article=current_object, image=img, title=img.name)
                del request.FILES[field_replace] #удаляем использованный файл
        if request.FILES: #Добавление нового изображения
            #print('!!!!!!!!!!!!!!!!!', request.FILES)
            for input_name in request.FILES:
                for img in request.FILES.getlist(input_name):
                    #print('###############', img)
                    Image.objects.create(article=current_object, image=img, title=img.name)


        return super(ArticleUpdateView, self).post(request, **kwargs)


class ArticleDeleteView(DeleteView):
    model = Article
    success_url = reverse_lazy('news_index')    #именованная ссылка или абсолютную
    template_name = 'news/delete_article.html'



from django.conf import settings
@login_required(login_url=settings.LOGIN_URL)
@check_group('Authors') #пример использования декоратора
def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            current_user = request.user
            if current_user.id != None: #проверили что не аноним
                new_article = form.save(commit=False)
                new_article.author = current_user
                new_article.date = datetime.date.today()
                new_article.save() #сохраняем в БД
                form.save_m2m() #сохраняем теги
                for img in request.FILES.getlist('image_field'):
                    Image.objects.create(article=new_article, image=img, title=img.name)
                return redirect('my_news_list')
    else:
        form = ArticleForm()
    return render(request, 'news/create_article.html', {'form': form})


from django.core.paginator import Paginator
def news_index(request):
    categories = Article.categories #создали перечень категорий
    author_list = User.objects.filter(article__isnull=False).filter(article__status=True).distinct() #создали перечень авторов
    selected_author = request.session.get('author_filter')
    selected_category = request.session.get('category_filter')
    selected_author = 0 if selected_author == None else selected_author
    selected_category = 0 if selected_category == None else selected_category

    if request.method == "POST":
        search_input = request.session.get('search_input')
        if search_input != None:  # если не пустое - находим нужные новости
            del request.session['search_input']  # чистим сессию, чтобы этот фильтр не "заело"
        selected_author = int(request.POST.get('author_filter'))
        selected_category = int(request.POST.get('category_filter'))
        request.session['author_filter'] = selected_author
        request.session['category_filter'] = selected_category
        return redirect('news_index')
    else: # Если метод запроса "GET", то:    # страница открывется впервые;    # нас переадресовала сюда функция поиска;    # листаем фильтрованные страницы (Paginator)

        # Фильтр по поиску
        search_input = request.session.get('search_input')  # вытаскиваем из сессии значение поиска
        #print('!!!!!!!!!!!!!!!!!!!!!!', 'search_input', search_input)
        if search_input != None:  # если не пустое - находим нужные новости
            articles = Article.objects.filter(title__icontains=search_input)
            selected_author = 0
            selected_category = 0
            #del request.session['search_input'] #чистим сессию, чтобы этот фильтр не "заело"
        else:   # если это не поисковый запрос, а переход по пагинатору или первое открытие
            articles = Article.objects.all()
            if selected_author != 0:  # если не пустое - находим нужные ноновсти
                articles = articles.filter(author=selected_author)
            if selected_category != 0:  # фильтруем найденные по авторам результаты по категориям
                articles = articles.filter(category__icontains=categories[selected_category - 1][0])

    # фильтр по публикации и сортировка от свежих к старым новостям
    articles = articles.filter(status='True').order_by('-date')
    total = len(articles)
    p = Paginator(articles, 6)
    page_number = request.GET.get('page')
    page_obj = p.get_page(page_number)
    context = {'articles': page_obj, 'author_list': author_list, 'selected_author': selected_author,
               'categories': categories, 'selected_category': selected_category, 'total': total}

    return render(request, 'news/index.html', context)


# вывод новостей по категориям, случейные 6
def main_index(request):
    articles = Article.objects.filter(status='True')
    it_articles = articles.filter(category__exact='IT').order_by('?')[:6]
    sport_articles = articles.filter(category__exact='SPORT').order_by('?')[:6]
    ai_articles = articles.filter(category__exact='AI').order_by('?')[:6]
    context = {'it_articles': it_articles, 'sport_articles': sport_articles, 'ai_articles': ai_articles}
    return render(request, 'main/index.html', context=context)