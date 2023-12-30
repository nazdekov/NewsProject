from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MaxLengthValidator

class Account(models.Model):
    gender_choices = [('M', 'Male'),
                     ('F', 'Female'),
                     ('N/A', 'Not answered')]
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                primary_key=True, verbose_name='Имя пользователя')
    nickname = models.CharField('Псевдоним', max_length=100,
                                validators=[MinLengthValidator(2), MaxLengthValidator(50)])
    birthdate = models.DateField(blank=True, null=True, verbose_name='Дата рождения')
    gender = models.CharField(choices=gender_choices, max_length=20, verbose_name='Пол')
    account_image = models.ImageField(default='default.jpg',
                                      upload_to='account_images')
    address = models.CharField(blank=True, null=True, max_length=100, verbose_name='Адрес',
                               validators=[MaxLengthValidator(50)])
    vk = models.CharField(blank=True, null=True, max_length=100, validators=[MaxLengthValidator(30)])
    instagram = models.CharField(blank=True, null=True, max_length=100, validators=[MaxLengthValidator(30)])
    telegram = models.CharField(blank=True, null=True, max_length=100, validators=[MaxLengthValidator(30)])
    phone = models.CharField(blank=True, null=True, max_length=20, verbose_name='Телефон')
    objects = models.Manager()
    #pip install pillow в терминале если нет библиотеки

    def __str__(self):
        return f"{self.user.username}'s account"

    class Meta:
        ordering = ['user']
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


from news.models import Article
class FavoriteArticle(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    article = models.ForeignKey(Article, on_delete=models.SET_NULL, null=True)
    create_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    def __str__(self):
        return self.article

    class Meta:
        verbose_name = 'Избранное'