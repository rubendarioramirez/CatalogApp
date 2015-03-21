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
	return render_template('catalog.html', categories=categories)
 
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

@app.route('/catalog/categoryname/items')
def categoryItems():
	return render_template('categoryitems.html')

@app.route('/catalog/categoryname/itemname')
def item():
	return render_template('item.html') 

@app.route('/catalog/categoryname/itemname/edit')
def itemEdit():
	return render_template('itemedit.html') 

@app.route('/catalog/categoryname/itemname/delete')
def itemDelete():
	return render_template('itemdelete.html') 

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)