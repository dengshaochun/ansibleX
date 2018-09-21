from django.db import models

# Create your models here.


class UserProfile(models.Model):
    ACCOUNT_CHOICES = (
        (1, '私有账号'),
        (2, '公共账号'),
        (3, '其他账号')
    )

    username = models.CharField(max_length=50)
    books = models.ManyToManyField('Book', through='UserBook')
    account_type = models.IntegerField('account type',
                                       choices=ACCOUNT_CHOICES,
                                       default=1)

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Book(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, related_name='books',
                                 on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.name


class UserBook(models.Model):

    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}:{1}'.format(self.user.username, self.book.name)
