import os
import json

from jinja2 import Environment, FileSystemLoader
from pdfkit import from_string


def create_pdf(template_name, template_variables, pdf_options, template_folder="templates"):
    env = Environment(loader=FileSystemLoader(searchpath=template_folder))
    template = env.get_template(template_name)
    html_out = template.render(template_variables)

    page = from_string(
        html_out,
        False,
        options=pdf_options,
        css=[] # its a list e.g ['my_css.css', 'my_other_css.css']
    )

    return page


def save_pdf(file_content):
    try:
        with open('output/your_pdf_file_here.pdf', 'wb+') as file:
            for chunk in file_content:
                file.write(chunk)

    except Exception as error:
        print(f'Error saving file to disc. Error: {error}')
        raise error
        
        
if __name__ == '__main__':
    template_vars = {
       'template_title': 'A template example',
       'template_description': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit'
    }
    pdf_options = {}
    pdf_file = create_pdf("file.html", template_vars, pdf_options)
    save_pdf(pdf_file)