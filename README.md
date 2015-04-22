# CatalogApp
Catalog Web application for UDACITY

The scope of this project is to create an application web based that stores data in SQLite, can fetch it and edit it.
You will see a simple catalog application, where you can browse per category and each category has their own items.
Also include login system that prevent non users to edit/add/delete content.

To run this project:

1) Copy the files from VagrantFiles folder (pg_config.sh and vagrantfile) to your vagrant environment.
2) Run Vagrant with the commands -vagrant up and -vagrant ssh
2) Initialize the database by running the command python catalogDataBaseSetup.py
3) Run the command python catalog.py
4) Now the catalog is running in your localhost:8000
5) The database it's empty, go to Create Category and then Create Item in order to populate the database
6) To retrieve a JSON file of all the item in one category please use : '/catalog/<int:category_id>/JSON' where INT:CATEGORY is the id of the category you want to see.

## In the case the Vagrant files are not working properly in your environment i recommend you to run the following PIP commands to ensure you have the right libs installed ###

pip install flask
pip install sqlalchemy
pip install requests
pip install oauth2client
pip install flask-seasurf

###LOGIN####
In order to Login you should
1) Connect to https://console.developers.google.com (If you dont have a gmail account get one)
2) Create a new project.
3) Download JSON file with your client secret credentials.
4) rename the file as client_secrets.json and ensure is located in the root folder of this project.
5) get your client ID and copy and paste it LOGIN.HTML (data-clientid="YOUR_CLIENT_ID_GOES_HERE")
