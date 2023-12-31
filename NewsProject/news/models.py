from django.db import models
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MaxLengthValidator
import datetime
import os
import shutil

from django.conf import settings

base_dir = settings.MEDIA_ROOT

class Tag(models.Model):
    title = models.CharField(max_length=80, verbose_name='Название')
    status = models.BooleanField(default=True, verbose_name='Статус')
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


from unidecode import unidecode
from django.template.defaultfilters import slugify
class Article(models.Model):
    categories = [('IT', 'IT'),
                  ('SPORT', 'Sport'),
                  ('AI', 'AI')]
    #поля                           #models.CASCADE SET_DEFAULT    # Если пользователь удалится, то удалятся все его новости
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Автор')    # Если пользователь удалится, то данное поле будет NULL
    title = models.CharField('Название', max_length=100, validators=[MinLengthValidator(10), MaxLengthValidator(100)])
    anouncement = models.TextField('Аннотация', max_length=250, validators=[MinLengthValidator(10), MaxLengthValidator(250)])
    text = models.TextField('Текст новости', validators=[MinLengthValidator(30), MaxLengthValidator(10000)])
    date = models.DateTimeField('Дата публикации', auto_created=True)
    date_edit = models.DateTimeField('Дата редактирования', auto_now=True)
    category = models.CharField(choices=categories, max_length=20, verbose_name='Категории')
    tags = models.ManyToManyField(to=Tag, blank=True, verbose_name='Тэги')    # blank - разрешаем полю быть пустым
    slug = models.SlugField()
    objects = models.Manager()
    published = PublishedToday()
    status = models.BooleanField(default=False, verbose_name='Опубликовано')    # Автор добавляет новость и по-умолчанию она не публикуется. Модетатор должен подтвердить публикацию - True


    #методы моделей
    def __str__(self):
        return f'{self.title} от: {str(self.date)[:16]}'

    def get_absolute_url(self):
        return f'/news/show/{self.id}'
    #метаданные модели


    def tag_list(self):
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
        article_dir = os.path.join(base_dir, dir_path)
        if os.path.exists(article_dir):
            shutil.rmtree(article_dir)

        super(Article, self).delete(*args, **kwargs)


    def save(self, *args, **kwargs):
        self.slug = slugify(unidecode(self.title))    # Генерирует Slug при создании или редактировании
        if not self.id:
            # Эта ветвь срабатыет при создании новости
            #self.slug = slugify(unidecode(self.title))
            pass

        super(Article, self).save(*args, **kwargs)


    class Meta:
        ordering = ['date', 'title']    # Порядок сортировки
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'


class Image(models.Model):
    def folder_path(instance, filename):
        return f"article_images/article_{instance.article.pk}/{filename}"

    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name='Новость')
    title = models.CharField(max_length=50, blank=True, verbose_name='Название')
    #image = models.ImageField(upload_to='article_images/')    # лучше добавить поле default !!!
    image = models.ImageField(upload_to=folder_path)     # лучше добавить поле default !!!  # default='default_article_img.png',
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
                                related_name='views', verbose_name='Новость')
    ip_address = models.GenericIPAddressField(verbose_name='IP-адрес')
    view_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата просмотра')
    objects = models.Manager()

    class Meta:
        verbose_name = 'Счетчик просмотров'
        verbose_name_plural = 'Счетчик просмотров'
        ordering = ('-view_date',)
        indexes = [models.Index(fields=['-view_date'])]

    def __str__(self):
        return self.article.title