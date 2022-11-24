from django.db.models import F, Sum
from rest_framework import status
from rest_framework.response import Response

from recipes.models import RecipeIngredient


def alter_model_related_with_user(
        request, field_name, instance,
        relation_model_cls, relation_szr_cls, instance_szr_cls
):
    user = request.user
    szr_context = {'request': request}

    if request.method == 'POST':

        data = {'user': user.pk, field_name: instance.pk}
        related_instance_szr = relation_szr_cls(
            data=data, context=szr_context
        )

        related_instance_szr.is_valid(raise_exception=True)
        related_instance_szr.save()
        user_serializer = instance_szr_cls(
            instance=instance, context=szr_context
        )
        return Response(
            user_serializer.data, status=status.HTTP_200_OK
        )

    filter_params = {'user': user, field_name: instance.pk}
    relation_model_cls.objects.filter(**filter_params).delete()

    return Response(status=status.HTTP_204_NO_CONTENT)


def create_shopping_cart(user):
    shopping_cart_queryset = RecipeIngredient.objects.filter(
        recipe__pk__in=(user.shopping_cart.values('recipe__pk'))
    ).values(
        name=F('ingredient__name'),
        measurement_unit=F('ingredient__measurement_unit')
    ).annotate(amount=Sum('amount'))

    return '\n'.join(
        (f'{ingredient["name"]}, {ingredient["measurement_unit"]} - '
         f'{ingredient["amount"]}')
        for ingredient in shopping_cart_queryset
    )
