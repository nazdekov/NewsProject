def get_client_ip(request):
    x_forwrded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwrded_for:
        ip = x_forwrded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


from .models import ViewCount
class ViewCountMixin:
    def get_object(self):
        #получаем объект из родительского класса
        obj = super().get_object()
        ip_address = get_client_ip(self.request)
        #Если такой счетчик уже создан - выполнится get - получение
        #если его еще не было - выполнится Create
        ViewCount.objects.get_or_create(article=obj, ip_address=ip_address)
        return obj


# from users.models import FavoriteArticle
# class FavoriteUsersMixin:
#     def get_users(self):
#         users = super().get_users()
#
#         bookmark = FavoriteArticle.objects.filter(article=current_object.pk)

# class RequestMixin: #(object):
#     """ Generic mixin to pass request data into context. """
#     def get_context_data(self, **kwargs):
#         context = super(RequestMixin, self).get_context_data(**kwargs)
#         context['request'] = self.request
#         return context
#