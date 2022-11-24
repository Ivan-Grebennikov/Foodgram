from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from utils.services import user_related_field_handler

from .models import Subscription, User
from .serializers import FollowingUserSerializer, SubscriptionSerializer


class SubscriptionViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()

    @action(detail=True, methods=('POST', 'DELETE'),
            permission_classes=(permissions.IsAuthenticated,))
    def subscribe(self, request, pk):

        return user_related_field_handler(
            request=request,
            field_name='following',
            instance=self.get_object(),
            relation_model_cls=Subscription,
            relation_szr_cls=SubscriptionSerializer,
            instance_szr_cls=FollowingUserSerializer,
        )

    @action(detail=False, methods=('GET',),
            permission_classes=(permissions.IsAuthenticated,),
            serializer_class=FollowingUserSerializer)
    def subscriptions(self, request):
        user = request.user

        followings = User.objects.filter(
            pk__in=Subscription.objects.filter(
                user=user).values_list('following', flat=True)
        )

        page = self.paginate_queryset(followings)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(instance=followings, many=True)
        return Response(serializer.data)
