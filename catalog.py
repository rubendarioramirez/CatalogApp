from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from catalogDataBaseSetup import Base, Category, CategoryItem

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#Main page - Function to display categories
@app.route('/')
def catalogMain():
	categories = session.query(Category).all()
	items = session.query(CategoryItem).all()
	return render_template('catalog.html', categories=categories, items=items)
 
#Add new category function
@app.route('/catalog/addcategory', methods=['GET','POST'])
def addCategory():
	if request.method == 'POST':
		newCategory = Category(name = request.form['name'])
		session.add(newCategory)
		session.commit()
		flash("New menu item created!")
		return redirect(url_for('catalogMain'))
	else:
		return render_template('addcategory.html')

#Add new item function
@app.route('/catalog/additem', methods=['GET','POST'])
def addItem():
	if request.method == 'POST':
		newItem = CategoryItem(name = request.form['name'], description = request.form['description'], price = request.form['price'], category_id = request.form['category'])
		session.add(newItem)
		session.commit()
		flash("New item created!")
		return redirect(url_for('catalogMain'))
	else:
		categories = session.query(Category).all()
		return render_template('additem.html',categories=categories)

#All items for an specific category
@app.route('/catalog/<int:category_id>/items')
def categoryItems(category_id):
	items = session.query(CategoryItem).filter_by(category_id = category_id)
	return render_template('categoryitems.html', items = items)

#Check specific item on specific category
@app.route('/catalog/<int:category_id>/<int:item_id>')
def item(category_id, item_id):
	item = session.query(CategoryItem).filter_by(id = item_id).one()
	return render_template('item.html', item = item) 

#Edit specific item
@app.route('/catalog/<int:category_id>/<int:item_id>/edit', methods=['GET','POST'])
def itemEdit(category_id, item_id):
	editedItem = session.query(CategoryItem).filter_by(id = item_id).one()
	if request.method == 'POST':
		if request.form['name']:
			editedItem.name = request.form['name']
			editedItem.description = request.form['description']
			editedItem.price = request.form['price']
			editedItem.category_id = request.form['category']
			session.add(editedItem)
			session.commit()
			flash("Item has been editted!")
			return redirect(url_for('catalogMain'))
		else:
			item = session.query(CategoryItem).filter_by(id = item_id).one()
			categories = session.query(Category).all()
			return render_template('itemedit.html', item = item, categories = categories) 

#Delete specific item
@app.route('/catalog/categoryname/itemname/delete')
def itemDelete():
	return render_template('itemdelete.html') 

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)