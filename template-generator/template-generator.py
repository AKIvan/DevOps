import yaml
from jinja2 import Environment, FileSystemLoader
import os
import logging
import argparse

logging.basicConfig(level=logging.INFO)

def gen_template(pipeline):
    dir_path = os.getcwd()
    try:
        with open(f'{dir_path}/conf/{pipeline}') as file:
            conf_var = yaml.load(file, Loader=yaml.FullLoader)

        file_loader = FileSystemLoader([os.path.join(dir_path, 'templates')])

        env = Environment(loader=file_loader)
        jinja_template = env.get_template(conf_var['template_path'])
        output = jinja_template.render(conf_var)
        return output
    except Exception as err:
        logging.info("Can't generate pipeline")
        logging.info(err)


parser = argparse.ArgumentParser(description='Generate or deploy AWS Stack')
parser.add_argument("--gen-template", help="Generate pipeline",
                    type=gen_template,
                    action="store")
args = parser.parse_args()

if args.gen_template:
    print(args.gen_template)
else:
    logging.info("Something is not right ...")