from django.db import models
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from django.db.models import Count
import datetime
import os
import shutil

from django.conf import settings

base_dir = settings.MEDIA_ROOT

class Tag(models.Model):
    title = models.CharField(max_length=80)
    status = models.BooleanField(default=True)
    def __str__(self):
        return self.title

    def tag_count(self):
        count = self.article_set.count()
        #комментарий: когда мы работаем со связанными объектами (foreign_key, m2m, один к одному),
        #мы можем обращаться к связанным таблицам при помощи синтаксиса:
        #связанная Модель_set и что-то делать с результатами. В этом примере - мы используем связанные article
        #и вызываем метод count
        return count

    class Meta:
        ordering = ['title', 'status']
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

class PublishedToday(models.Manager):
    def get_queryset(self):
        return super(PublishedToday, self).get_queryset().filter(date__gte=datetime.date.today())

class Article(models.Model):
    categories = [('IT', 'IT'),
                  ('MATH', 'Mathematic'),
                  ('AI', 'AI')]
    #поля                           #models.CASCADE SET_DEFAULT    # Если пользователь удалится, то удалятся все его новости
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Автор')    # Если пользователь удалится, то данное поле будет NULL
    title = models.CharField('Название', max_length=50, default='')
    anouncement = models.TextField('Аннотация', max_length=250)
    text = models.TextField('Текст новости')
    date = models.DateTimeField('Дата публикации', auto_now=True)
    date_edit = models.DateTimeField('Дата редактирования', auto_now=True)
    category = models.CharField(choices=categories, max_length=20, verbose_name='Категории')
    tags = models.ManyToManyField(to=Tag, blank=True, verbose_name='Тэги')    # blank - разрешаем полю быть пустым
    slug = models.SlugField()
    objects = models.Manager()
    published = PublishedToday()
    status = models.BooleanField(default=False, verbose_name='Опубликовать')    # Автор добавляет новость и по-умолчанию она не публикуется. Модетатор должен подтвердить публикацию - True

    #методы моделей
    def __str__(self):
        return f'{self.title} от: {str(self.date)[:16]}'

    def get_absolute_url(self):
        return f'/news/show/{self.id}'
    #метаданные модели


    def tag_list(self):    # не работает, пока что
        s = ''
        for t in self.tags.all():
            s += '|' + t.title + ' '
        return s

    def image_tag(self):
        image = Image.objects.filter(article=self)
        if image:
            return mark_safe(f'<img src="{image[0].image.url}" height="50px" width="auto" />')
        else:
            return '(no image)'

    def get_views(self):
        return self.views.count()

    def delete(self, *args, **kwargs):
        """для автоматического удаления папки с изображениями статьи"""
        dir_path = f"article_images/article_{self.pk}"
        ar_dir = os.path.join(base_dir, dir_path)
        if os.path.exists(ar_dir):
            shutil.rmtree(ar_dir)

        super(Article, self).delete(*args, **kwargs)


    class Meta:
        ordering = ['title', 'date']    # Порядок сортировки
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'


class Image(models.Model):
    def folder_path(instance, filename):
        return f"article_images/article_{instance.article.pk}/{filename}"

    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, blank=True)
    #image = models.ImageField(upload_to='article_images/')    # лучше добавить поле default !!!
    image = models.ImageField(upload_to=folder_path)     # лучше добавить поле default !!!
    objects = models.Manager()

    def __str__(self):
        return self.title

    def image_tag(self):
        if self.image is not None:
            return mark_safe(f'<img src="{self.image.url}" height="50px" width="auto" />')
        else:
            return '(no image)'

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'



class ViewCount(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE,
                                related_name='views')
    ip_address = models.GenericIPAddressField()
    view_date = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    class Meta:
        ordering = ('-view_date',)
        indexes = [models.Index(fields=['-view_date'])]

    def __str__(self):
        return self.article.title