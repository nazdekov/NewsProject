from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, HttpResponse
from django.template.loader import get_template

from .forms import ContactForm
from django.conf import settings
import git
from django.views.decorators.csrf import csrf_exempt
import hashlib
import hmac
from django.http import HttpResponseServerError

#
# def verify_signature(payload_body, secret_token, signature_header):
#     """Verify that the payload was sent from GitHub by validating SHA256.
#
#     Raise and return 403 if not authorized.
#
#     Args:
#         payload_body: original request body to verify (request.body())
#         secret_token: GitHub app webhook token (WEBHOOK_SECRET)
#         signature_header: header received from GitHub (x-hub-signature-256)
#     """
#     if not signature_header:
#         return HttpResponseServerError("x-hub-signature-256 header is missing!", status=403)
#     hash_object = hmac.new(secret_token.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
#     expected_signature = "sha256=" + hash_object.hexdigest()
#     if not hmac.compare_digest(expected_signature, signature_header):
#         return HttpResponseServerError("Request signatures didn't match!", status=403)



@csrf_exempt
def update_server(request):
    # header_signature = request.META.get('HTTP_X_HUB_SIGNATURE')
    # verify_signature(request.body, settings.GITHUB_WEBHOOK_KEY, header_signature)
    if request.method == "POST":
        local_dir = '/home/nazdekov/NewsProject/'    # local dir это где лежит .git
        repo = git.Repo(local_dir)
        repo.remotes.origin.pull()
        return HttpResponse("PythonAnywhere server updated successfully")
    else:
        return HttpResponse("Вы попали не туда")


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
    context = {}
    return render(request, 'main/404.html', context)

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

