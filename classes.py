from dataclasses import dataclass
from typing import Optional
from jinja2 import Environment, FileSystemLoader


class HasID:
    """
    Abstract class for items with an ID
    """
    instances: dict[str, "HasID"]
    id_field: str = "name"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if getattr(self, self.id_field) in self.instances:
            raise ValueError(f"Duplicate {self.id_field} value")
        self.instances[getattr(self, self.id_field)] = self
    
    @property
    def id(self):
        return getattr(self, self.id_field)

    @classmethod
    def get_by_id(cls, id_value):
        if id_value not in cls.instances:
            raise ValueError(f"No {cls.__name__} with {cls.id_field} {id_value}")
        return cls.instances.get(id_value)
    
    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        cls.instances[getattr(instance, cls.id_field)] = instance
        return instance
    
    @classmethod
    def get_or_create(cls, **kwargs):
        id_value = kwargs.get(cls.id_field)
        if id_value in cls.instances:
            return cls.instances.get(id_value)
        return cls.create(**kwargs)


class HasTemplate:
    """
    Abstract class for items with a template
    """
    template: str

    def format_for_template(self) -> dict:
        raise NotImplementedError

    def get_html(self, page_number: Optional[int] = None) -> str:
        env = Environment(loader=FileSystemLoader(searchpath="templates"))
        template = env.get_template(self.template)
        template_vars = self.format_for_template()
        if page_number:
            template_vars["page_number"] = page_number
        return template.render(template_vars)


@dataclass
class Category(HasTemplate, HasID):
    """
    Category dataclass
    
    Attributes:
        - name: name of the category
        - arabic_name: name of the category in arabic
        - recipes: list of recipes
    """
    instances = {}
    name: str
    arabic_name: str
    order: int
    template: str = "category.html"

    @classmethod
    def batch_create(cls, data: list[dict]):
        instances = []
        for category in data:
            instance = cls.create(
                name=category["name"],
                arabic_name=category["arabic_name"],
                order=category["order"]
            )
            instances.append(instance)
        return instances
    
    def format_for_template(self) -> dict:
        return {
            "name": self.name,
            "arabic_name": self.arabic_name,
        }
            


@dataclass
class Ingredient(HasID):
    """
    Ingredient dataclass
    
    Attributes:
        - name: name of the ingredient
    """
    instances = {}
    name: str


@dataclass
class IngredientQuantity:
    """
    IngredientQuantity dataclass
    
    Attributes:
        - ingredient: ingredient
        - quantity: quantity of the ingredient
    """
    ingredient: Ingredient
    quantity: str

    @classmethod
    def batch_create(cls, data: list[dict]):
        instances = []
        for ingredient_quantity in data:
            instance = cls(
                ingredient=Ingredient.get_or_create(
                    name=ingredient_quantity["name"]
                ),
                quantity=ingredient_quantity["quantity"]
            )
            instances.append(instance)
        return instances


@dataclass
class Recipe(HasTemplate, HasID):
    """
    Recipe dataclass
    
    Attributes:
        - name: name of the meal
        - arabic_name: name of the meal in arabic
        - servings: number of servings
        - ingredients: list of ingredients and their quantities
        - instructions: list of instructions
    """
    instances = {}
    order: int
    category: Category
    name: str
    arabic_name: str
    image_path: str
    description: str
    servings: int
    ingredients: list[IngredientQuantity]
    instructions: list[str]
    template: str = "recipe.html"

    def __str__(self):
        return self.name
    
    def format_for_template(self) -> dict:
        return {
            "name": self.name,
            "arabic_name": self.arabic_name,
            "image_path": self.image_path,
            "description": self.description,
            "servings": self.servings,
            "ingredients": [i.quantity for i in self.ingredients],
            "instructions": self.instructions,
        }

    def has_ingredient(self, ingredient: Ingredient) -> bool:
        return any(
            ingredient_quantity.ingredient == ingredient
            for ingredient_quantity in self.ingredients
        )
    
    def is_in_category(self, category: Category) -> bool:
        return self.category == category
    
    @classmethod
    def get_by_categories(cls) -> list[dict]:
        categories = Category.instances.values()
        recipes_by_category = {category.name: {"category": category, "recipes": []} for category in categories}
        for recipe in sorted(list(cls.instances.values()), key=lambda x: x.order):
            recipes_by_category[recipe.category.name]["recipes"].append(recipe)
        recipes_by_category = list(recipes_by_category.values())
        return sorted(recipes_by_category, key=lambda x: x["category"].order)
    
    @classmethod
    def get_by_ingredients(cls) -> list[dict]:
        ingredients = Ingredient.instances.values()
        recipes_by_ingredient = {ingredient.name: {"ingredient": ingredient, "recipes": []} for ingredient in ingredients}
        for recipe in sorted(cls.instances.values(), key=lambda x: x.name):
            for ingredient in ingredients:
                if recipe.has_ingredient(ingredient):
                    recipes_by_ingredient[ingredient.name]["recipes"].append(recipe)
        recipes_by_ingredient = list(recipes_by_ingredient.values())
        return sorted(recipes_by_ingredient, key=lambda x: x["ingredient"].name)

    @classmethod
    def batch_create(cls, data: list[dict]):
        instances = []
        for recipe in data:
            instance = cls.create(
                order=recipe["order"],
                category=Category.get_by_id(recipe["category"]),
                name=recipe["name"],
                arabic_name=recipe["arabic_name"],
                image_path=recipe["image_path"],
                description=recipe["description"],
                servings=recipe["servings"],
                ingredients=IngredientQuantity.batch_create(recipe["ingredients"]),
                instructions=recipe["instructions"],
            )
            instances.append(instance)
        return instances
