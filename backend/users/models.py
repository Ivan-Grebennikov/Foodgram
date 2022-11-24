from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Meta(AbstractUser.Meta):
        ordering = ('date_joined',)
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following', verbose_name='User',
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='follower', verbose_name='Following',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'following'], name='unique_subscription'),
        )
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'

    def __str__(self):
        return f'{self.user} -> {self.following}'
