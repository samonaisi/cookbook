import json
from typing import List

from jinja2 import Environment, FileSystemLoader
from pdfkit import from_string

from classes import Category, Recipe, Ingredient, IngredientQuantity


class CookBook:
    head_template = "head.html"

    @classmethod
    def get_head(cls) -> str:
        env = Environment(loader=FileSystemLoader(searchpath="templates"))
        template = env.get_template(cls.head_template)
        return template.render()

    @classmethod
    def get_pdf_data(cls, pages, pdf_options, css_list):
        pages = [cls.get_head(), *pages]
        return from_string(
            ''.join(pages),
            False,
            options=pdf_options,
            css=css_list # its a list e.g ['my_css.css', 'my_other_css.css']
        )

    @classmethod
    def save_pdf(cls, file_content):
        try:
            with open('output/output.pdf', 'wb+') as file:
                file.write(file_content)
        except Exception as error:
            print(f'Error saving pdf file : {error}')
            raise error
        
    @classmethod
    def create_pdf(cls, pages: list[str], pdf_options: dict, css_list: list[str]):
        """
        Create a pdf file from a list of pages
        
        Args:
            pages: list of pages to be included in the pdf
            pdf_options: dictionary of pdf options
            css_list: list of css files to be included in the pdf
        """
        pdf_data = cls.get_pdf_data(pages, pdf_options, css_list)
        cls.save_pdf(pdf_data)

        
if __name__ == '__main__':
    with open("data/categories.json") as file:
        categories = json.load(file)["categories"]
        Category.batch_create(categories)

    with open("data/recipes.json") as file:
        recipes = json.load(file)["recipes"]
        Recipe.batch_create(recipes)

    recipes_by_category = Recipe.get_by_categories()
    recipes_by_ingredient = Recipe.get_by_ingredients()
    pages = []
    page_number = 1
    for c in recipes_by_category:
        category: Category = c["category"]
        recipes: List[Recipe] = c["recipes"]
        pages.append(category.get_html(page_number))
        page_number += 1
        for recipe in recipes:
            pages.append(recipe.get_html(page_number))
            page_number += 1
    CookBook.create_pdf(pages, {"page-size": "A4"}, ["css/recipes.css"])
    