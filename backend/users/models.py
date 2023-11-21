from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name'
    )
    
    email = models.EmailField('Email адрес', max_length=254, unique=True)

    password = models.CharField(
        max_length=150,
        null=True,
        blank=False,
    )
    class Meta:
        ordering = ('id',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'


    def __str__(self):
        return self.username
    

class Subscribe(models.Model):
    """Модель подписки"""
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name="subscriber",
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
                name='unique_subscribe'
            ),
        )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
