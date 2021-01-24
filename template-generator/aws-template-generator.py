import yaml
from jinja2 import Environment, FileSystemLoader
import boto3
import os
import logging
import argparse
from git import Repo

logging.basicConfig(level=logging.INFO)

dir_path = os.getcwd()
# You can use the git branch name if the directory is from the git.
# repo = Repo(dir_path)
# branch = repo.active_branch
# branch_name = str(branch)

# Stack name is the directory of where the script will be executed
# stack_name = os.getcwd().split('/')[-1]


dir_path = os.getcwd()

def gen_template(fileconf):
    try:
        with open(f'{dir_path}/conf/{fileconf}') as file:
            conf_var = yaml.load(file, Loader=yaml.FullLoader)
        # conf_var['user_data']['branch'] = branch_name
        file_loader = FileSystemLoader([os.path.join(dir_path, 'templates')])
        env = Environment(loader=file_loader)
        jinja_template = env.get_template(conf_var['template_path'])
        output = jinja_template.render(conf_var)
        return output

    except Exception as err:
        logging.info("Can't generate pipeline")
        logging.info(err)


def save_template(template):
    gen_output = gen_template(template)
    with open(f'{dir_path}/{template}', "w") as fh:
        fh.write(gen_output)
    return gen_output


aws_profile = os.environ.get('AWS_PROFILE')


def aws_deploy(template, stack_name):
    try:
        gen_output = gen_template(template)
        client = boto3.client('cloudformation')
        response_deploy = client.create_stack(
            StackName=stack_name,
            TemplateBody=gen_output)
        logging.info(response_deploy)
        logging.info("Deployment in progress")
        return response_deploy
    except Exception as err:
        logging.info("Can't deploy to AWS")
        logging.info("Pleas login to aws cli")
        logging.info(err)


def delete_stack(stack_name):
    try:
        client = boto3.client('cloudformation')
        response_delete = client.delete_stack(
            StackName=stack_name
        )
        logging.info(response_delete)
        return response_delete
    except Exception as err:
        logging.info("Can't delete the stack")
        logging.info(err)


parser = argparse.ArgumentParser(description='Generate or deploy AWS Stack')
parser.add_argument("--gen-template", help="Generate pipeline",
                    type=gen_template,
                    action="store")
parser.add_argument("--save-template", help="Generate pipeline",
                    type=save_template,
                    action="store")

parser.add_argument("--aws-deploy", help="Deploy Stack to AWS",
                    type=str,
                    action="store")
parser.add_argument('--stack-name', help="Stack Name",
                    type=str
                    )

parser.add_argument("--delete-stack", help="Delete Stack to AWS",
                    type=str,
                    action="store")

args = parser.parse_args()

# logging.info(args)

if args.gen_template:
    print(args.gen_template)
elif args.aws_deploy:
    template = args.aws_deploy
    stack_name = args.stack_name
    if stack_name is None:
        logging.info("Pleas specify stack name using '--stack-name' option ")
    else:
        aws_deploy(template, stack_name)
elif args.save_template:
    print(args.save_template)
elif args.delete_stack:
    delete_stack(args.delete_stack)
else:
    logging.info("Choose an options")