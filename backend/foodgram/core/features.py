from datetime import datetime

from django.db.models import F, Sum

from recipes.models import AmountIngredient, Ingredient, Recipe
from users.models import User


def create_recipe_ingredients(
    recipe: Recipe, ingredients: dict[int, tuple["Ingredient", int]]
) -> None:
    """Записывает игредиенты в рецепт."""
    objs = []
    for ingredient, amount in ingredients.values():
        objs.append(
            AmountIngredient(
                recipe=recipe,
                amount=amount,
                ingredients=ingredient,
            )
        )
    AmountIngredient.objects.bulk_create(objs)


def create_shopping_list(user: User) -> str:
    """Создает список покупок."""
    shopping_list = [
        f"Список покупок для:\n\n{user.first_name}\n"
        f'{datetime.now().strftime("%d/%m/%Y %H:%M")}\n'
    ]
    ingredients = (
        AmountIngredient.objects.filter(recipe__in_carts__user=user)
        .values(
            "ingredients__name",
            measurement=F("ingredients__measurement_unit")
        )
        .annotate(amount=Sum("amount"))
    )

    ingredient_list = (
        f'{ing["ingredients__name"]}: {ing["amount"]} {ing["measurement"]}'
        for ing in ingredients
    )
    shopping_list.extend(ingredient_list)
    shopping_list.append("\nСоставлено в Foodgram")
    return "\n".join(shopping_list)
