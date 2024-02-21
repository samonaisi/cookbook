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
        
        
if __name__ == '__main__':
    template_vars = {
       'template_title': 'A template example',
       'template_description': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit'
    }
    pdf_options = {}
    page_1 = get_page_from_template("file.html", template_vars)
    page_2 = get_page_from_template("file.html", template_vars)
    pdf_data = get_pdf_data([page_1, page_2], pdf_options, [])
    save_pdf(pdf_data)