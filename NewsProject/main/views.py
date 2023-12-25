from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, HttpResponse
from django.template.loader import get_template

from .forms import ContactForm
import git

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def update_server(request):
    if request.method == "POST":
        link = 'https://github.com/nazdekov/NewsProject.git'
        repo = git.Repo(link)
        origin = repo.remotes.origin
        origin.pull()
        return HttpResponse('Updated pythonanywhere successfully')
    else:
        return HttpResponse('wrong event type')



#def index(request):
#    news_it = Article.objects.filter(category__exact='IT').order_by('?')[:6]
#    news_math = Article.objects.filter(category__exact='MATH').order_by('?')[:6]
#    news_ai = Article.objects.filter(category__exact='AI').order_by('?')[:6]
#    context = {'news_it': news_it, 'news_math': news_math, 'news_ai': news_ai}
#    return render(
#        request,
#        'main/index.html',
#        context=context
#    )

# def detail(request,id):
#     #пример итерирования по объектам QuerySet
#     newsitems = NewsItem.objects.all()
#     s = ''
#     for newsitem in newsitems:
#         if id == newsitem.id:
#             s += f'<h1>{newsitem.title}</h1><br> <p> Страница на доработке </p>'
#     return HttpResponse(s)

def about(request):
    return render(
        request,
        'main/about.html'
    )


def contacts(request):
    context = {}
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            send_message(form.cleaned_data['name'], form.cleaned_data['email'], form.cleaned_data['message'])
            context = {'success': 1}
    else:
        form = ContactForm()
    context['form'] = form
    return render(
        request,
        'main/contacts.html',
        context=context
    )


def send_message(name, email, message):
    text = get_template('main/message.html')
    html = get_template('main/message.html')
    context = {'name': name, 'email': email, 'message': message}
    subject = 'Сообщение от пользователя'
    from_email = 'from@example.com'
    text_content = text.render(context)
    html_content = html.render(context)

    msg = EmailMultiAlternatives(subject, text_content, from_email, ['manager@example.com'])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

def custom_404(request, exception):
    return HttpResponse(f'Вот-так-так! Что-то пошло не так: {exception}')

def get_calc(request, a, operation, b):
    match operation:                    # match - это вместо if, elif, else
        case 'plus':
            result = int(a) + int(b)
        case 'minus':
            result = int(a) - int(b)
        case 'multiply':
            result = int(a) * int(b)
        case 'divide':
            result = int(a) / int(b)
        case 'power':
            result = int(a) ** int(b)
        case _:
            return HttpResponse(f'Неизвестная команда.')
    return HttpResponse(f'Вы ввели: {a} и {b}<br>Результат "{operation}": {result}.')

