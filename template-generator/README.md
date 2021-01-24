# TEMPLATE GENERATORS

**template-generator** is a Python tool using Jinja2 that can help you, from the configuration file in the conf directory to render different templates.
You can render any kind of files. In the configuration directory("conf"), you create an yaml file that have the configuration variables needed to generate a template.
This yaml file is a dictionary that starts with two main variables.
1. "template_path": that contains the name of the file/template that need to be render
2. "user_data": that contains all the other variables for the template. 


**aws-template-generator** have additional options to deploy, save and delete the stack if needed.

* Note: They are very basic but still can be very useful. - still in developing