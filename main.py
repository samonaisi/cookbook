import os
import json

from jinja2 import Environment, FileSystemLoader
from pdfkit import from_string


def get_page_from_template(template_name, template_variables, template_folder="templates"):
    env = Environment(loader=FileSystemLoader(searchpath=template_folder))
    template = env.get_template(template_name)
    return template.render(template_variables)


def get_pdf_data(pages, pdf_options, css_list):
    return from_string(
        ''.join(pages),
        False,
        options=pdf_options,
        css=css_list # its a list e.g ['my_css.css', 'my_other_css.css']
    )


def save_pdf(file_content):
    try:
        with open('output/output.pdf', 'wb+') as file:
            file.write(file_content)

    except Exception as error:
        print(f'Error saving file to disc. Error: {error}')
        raise error
    

def get_pages():
    with open("data/pages.json") as file:
        return json.load(file)["pages"]
        
        
if __name__ == '__main__':
    pages = []
    for page_number, page_data in enumerate(get_pages()):
        page_data = {
            "page_number": page_number,
            **page_data
        }
        template = page_data["type"]
        pages.append(get_page_from_template(f"{template}.html", page_data))
    pdf_options = {}
    pdf_data = get_pdf_data(pages, pdf_options, ["css/recipes.css"])
    save_pdf(pdf_data)