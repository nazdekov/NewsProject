from django.urls import path
import news.views as news_views
from . import views

urlpatterns = [
    path('', news_views.main_index, name='home'),
    path('update_server/', views.update_server, name='update_server'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    # path('calc/<int:a>/<slug:operation>/<int:b>', views.get_calc),
]



