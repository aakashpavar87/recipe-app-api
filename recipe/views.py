"""
Views for Recipes.
"""

from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
    extend_schema_view,
)
from rest_framework import mixins, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Ingredient, Recipe, Tag
from recipe.serializers import (
    IngredientSerializer,
    RecipeDetailSerializer,
    RecipeImageSerializer,
    RecipeSerializer,
    TagSerializer,
)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "tags", OpenApiTypes.STR, description="Comma separated value for tags."
            ),
            OpenApiParameter(
                "ingredients",
                OpenApiTypes.STR,
                description="Comma separated value for ingredients.",
            ),
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """View Set for Recipe APIs."""

    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """Converts comma separeted string to integer."""
        return [int(param) for param in qs.split(",")]

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        ingredients = self.request.query_params.get("ingredients")
        tags = self.request.query_params.get("tags")
        queryset = self.queryset

        if tags:
            tags_list = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tags_list)

        if ingredients:
            ingredient_list = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_list)

        return queryset.filter(user=self.request.user).order_by("-id").distinct()

    def get_serializer_class(self):
        """Retrieve appropriate serializer class according to action."""
        if self.action == "list":
            return RecipeSerializer
        elif self.action == "upload_image":
            return RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create New Recipe With Current Logged In User."""
        serializer.save(user=self.request.user)

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        """Custom Action for handling upload image API."""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseRecipeAttrViewSet(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve Tags for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by("-name")


class TagViewSet(BaseRecipeAttrViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Views for Ingredient."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
