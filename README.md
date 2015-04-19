# CatalogApp
Catalog Web application for UDACITY

The scope of this project is to create an application web based that stores data in SQLite, can fetch it and edit it.
You will see a simple catalog application, where you can browse per category and each category has their own items.
Also include login system that prevent non users to edit/add/delete content.

To run this project:
1) Run Vagrant (Using the commands Vagrant Up to start and then Vagran SSH to start the console)
2) Initialize the database by running the command python catalogDataBaseSetup.py
3) Run the command python catalog.py
4) Now the catalog is running in your localhost/8000
5) The database it's empty, go to Create Category and then Create Item in order to populate the database
6) To retrieve a JSON file of all the item in one category please use : '/catalog/<int:category_id>/JSON' where INT:CATEGORY is the id of the category you want to see.
7) You are able to login by using Gmail account.


