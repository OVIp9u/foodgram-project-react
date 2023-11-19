from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

class User(AbstractUser):
    """Модель пользователя."""
    username = models.CharField(
        'Username',
        max_length=150,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Имя пользователя содержит недопустимый символ'
        )]
    )
    email = models.EmailField('Email адрес', max_length=254, unique=True)

    first_name = models.CharField(
        max_length=150,

    )
    last_name = models.CharField(
        max_length=150,
        null=True,
        blank=False,
    )
    password = models.CharField(
        max_length=150,
        null=True,
        blank=False,
    )

    def __str__(self):
        return self.username
    

class Subscribe(models.Model):
    """Модель подписки"""
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name="subscriber",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='subscribing',
        on_delete=models.CASCADE,
    )
    
    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription'
            ),
        )
