from django.db import models

# from django.contrib.auth.models import User
#
# class Tag(models.Model):
#     title = models.CharField(max_length=80)
#     status = models.BooleanField(default=True)
#     def __str__(self):
#         return self.title
#     class Meta:
#         ordering = ['title', 'status']
#         verbose_name = 'Тэг'
#         verbose_name_plural = 'Тэги'
#
#
#
# class NewsItem(models.Model):
#     categories = (('IT', 'IT'),
#                   ('MATH', 'Mathematic'),
#                   ('AI', 'AI'))
#     #поля                           #models.CASCADE SET_DEFAULT
#     author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     title = models.CharField('Название', max_length=50, default='')
#     anouncement = models.TextField('Аннотация', max_length=250)
#     text = models.TextField('Текст новости')
#     date = models.DateTimeField('Дата публикации', auto_now=True)
#     category = models.CharField(choices=categories, max_length=20, verbose_name='Категории')
#     tags = models.ManyToManyField(to=Tag, blank=True)
#     image = models.ImageField(upload_to='news_images', verbose_name='Изображение', default='default.png')
#
#     #методы моделей
#     def __str__(self):
#         return f'{self.title} от: {str(self.date)[:16]}'
#
#     def get_absolute_url(self):
#         return f'/show/{self.id}'
#     #метаданные модели
#
#
#     def tag_list(self):
#         s = ''
#         for t in self.tags.all():
#             s += t.title+' '
#         return s
#
#     class Meta:
#         ordering = ['title', 'date']
#         verbose_name = 'Новость'
#         verbose_name_plural = 'Новости'
#