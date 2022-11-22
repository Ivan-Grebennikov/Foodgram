from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Meta(AbstractUser.Meta):
        ordering = ('date_joined',)


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'following'], name='unique_subscription'),
        )

    def __str__(self):
        return f'{self.user} -> {self.following}'
