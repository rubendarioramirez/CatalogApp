from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

### Anti CSRF Helper import ###
from flask.ext.seasurf import SeaSurf
### Make the app an object of SeaSurf to protect from CSRF
csrf = SeaSurf(app)

## IMPORT FOR LOGIN ####
from flask import session as login_session
import random, string

### IMPORT FOR AUTHENTICATION ####
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from oauth2client.client import AccessTokenCredentials
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME= "Catalog App"

### Import and config for picture upload ####
import os
from werkzeug import secure_filename
UPLOAD_FOLDER = 'static/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

### Import to perform CRUD actions in the database ####
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from catalogDataBaseSetup import Base, Category, CategoryItem, User

engine = create_engine('sqlite:///catalogUpdated.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#Main page - Function to display categories
@app.route('/')
def catalogMain():
	categories = session.query(Category).all()
	items = session.query(CategoryItem).all()
	return render_template('catalog.html', categories=categories, items=items)

##Main G+ login function ###
@app.route('/login')
def showLogin():
  state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
  login_session['state'] = state
  #return "The current session state is %s" % login_session['state']
  return render_template('login.html', STATE = state)

##Gconnect is exempt of CSRF for login purposes.
@csrf.exempt
@app.route('/gconnect', methods=['POST'])
def gconnect():
  
  #print 'received state of %s' %request.args.get('state')
  #print 'login_sesion["state"] = %s' %login_session['state']
  if request.args.get('state') != login_session['state']:
    response = make_response(json.dumps('Invalid state parameter.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
  
  #gplus_id = request.args.get('gplus_id')
  #print "request.args.get('gplus_id') = %s" %request.args.get('gplus_id')
  code = request.data
  print "received code of %s " % code

  try:
    # Upgrade the authorization code into a credentials object
    oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
    oauth_flow.redirect_uri = 'postmessage'
    credentials = oauth_flow.step2_exchange(code)
  except FlowExchangeError:
    response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
  
  # Check that the access token is valid.
  access_token = credentials.access_token
  url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
         % access_token)
  h = httplib2.Http()
  result = json.loads(h.request(url, 'GET')[1])
  # If there was an error in the access token info, abort.
  if result.get('error') is not None:
    response = make_response(json.dumps(result.get('error')), 500)
    response.headers['Content-Type'] = 'application/json'
 
  # Verify that the access token is used for the intended user.
  gplus_id = credentials.id_token['sub']
  if result['user_id'] != gplus_id:
    response = make_response(
        json.dumps("Token's user ID doesn't match given user ID."), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
  # Verify that the access token is valid for this app.

  if result['issued_to'] != CLIENT_ID:
    response = make_response(
        json.dumps("Token's client ID does not match app's."), 401)
    print "Token's client ID does not match app's."
    response.headers['Content-Type'] = 'application/json'
    return response

  stored_credentials = login_session.get('credentials')
  stored_gplus_id = login_session.get('gplus_id')
  if stored_credentials is not None and gplus_id == stored_gplus_id:
    response = make_response(json.dumps('Current user is already connected.'),
                             200)
    response.headers['Content-Type'] = 'application/json'
    
  # Store the access token in the session for later use.
  login_session['provider'] = 'google'
  login_session['access_token'] = credentials.access_token
  login_session['gplus_id'] = gplus_id
  response = make_response(json.dumps('Successfully connected user.', 200))
  
  print "#Get user info"
  userinfo_url =  "https://www.googleapis.com/oauth2/v1/userinfo"
  params = {'access_token': credentials.access_token, 'alt':'json'}
  answer = requests.get(userinfo_url, params=params)
  data = json.loads(answer.text)
  
  #login_session['credentials'] = credentials
  #login_session['gplus_id'] = gplus_id
  login_session['username'] = data["name"]
  login_session['picture'] = data["picture"]
  login_session['email'] = data["email"]
  #print login_session['email']

  # Verify that the access token is used for the intended user.
  gplus_id = credentials.id_token['sub']
  if result['user_id'] != gplus_id:
    response = make_response(
        json.dumps("Token's user ID doesn't match given user ID."), 401)
    response.headers['Content-Type'] = 'application/json'
    return response


  output = ''
  output +='<h1>Welcome, '
  output += login_session['username']

  output += '!</h1>'
  output += '<img src="'
  output += login_session['picture']
  output +=' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
  flash("you are now logged in as %s"%login_session['username'])
  return output

#User Helper Functions
def createUser(login_session):
  newUser = User(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])
  session.add(newUser)
  session.commit()
  user = session.query(User).filter_by(email = login_session['email']).one()
  return user.id

def getUserInfo(user_id):
  user = session.query(User).filter_by(id = user_id).one()
  return user

def getUserID(email):
  try:
      user = session.query(User).filter_by(email = email).one()
      return user.id
  except:
      return None

#DISCONNECT - Revoke a current user's token and reset their login_session
#Revoke current user's token and reset their login_session.
@app.route("/gdisconnect")
def gdisconnect():
  
  # Only disconnect a connected user.
  credentials = login_session.get('access_token')
  if credentials is None:
    response = make_response(json.dumps('Current user not connected.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response

  # Execute HTTP GET request to revoke current token.
  access_token = login_session.get('access_token')
  url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
  h = httplib2.Http()
  result = h.request(url, 'GET')[0]

  if result['status'] == '200':
    # Reset the user's session.
    del login_session['access_token']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    response = make_response(json.dumps('Successfully disconnected.'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response
  else:
    # For whatever reason, the given token was invalid.
    response = make_response(
        json.dumps('Failed to revoke token for given user.', 400))
    response.headers['Content-Type'] = 'application/json'
    return response
 
#Add new category function
@app.route('/catalog/addcategory', methods=['GET','POST'])
def addCategory():
	if 'username' not in login_session:
		return redirect('/login')
	if request.method == 'POST':
		newCategory = Category(name = request.form['name'])
		session.add(newCategory)
		session.commit()
		flash("New menu item created!")
		return redirect(url_for('catalogMain'))
	else:
		return render_template('addcategory.html')

### Determine if the fileuploaded it's allowed ###
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#Add new item function
@app.route('/catalog/additem', methods=['GET','POST'])
def addItem():
  if 'username' not in login_session:
    return redirect('/login')
  if request.method == 'POST':
    file = request.files['file']
    if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      newItem = CategoryItem(name = request.form['name'], description = request.form['description'], price = request.form['price'], picture = filename, category_id = request.form['category'])
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
	category = session.query(Category).filter_by(id = category_id).one()
	items = session.query(CategoryItem).filter_by(category_id = category_id)
	return render_template('categoryitems.html', items = items, category = category)

#Check specific item on specific category
@app.route('/catalog/<int:category_id>/<int:item_id>')
def item(category_id, item_id):
	item = session.query(CategoryItem).filter_by(id = item_id).one()
	return render_template('item.html', item = item) 

#Edit specific item
@app.route('/catalog/<int:category_id>/<int:item_id>/edit', methods=['GET','POST'])
def itemEdit(category_id, item_id):
	if 'username' not in login_session:
		return redirect('/login')
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
@app.route('/catalog/<int:category_id>/<int:item_id>/delete', methods = ['GET','POST'] )
def itemDelete(category_id, item_id):
	if 'username' not in login_session:
		return redirect('/login')
	itemToDelete = session.query(CategoryItem).filter_by(id = item_id).one() 
	if request.method == 'POST':
		session.delete(itemToDelete)
		session.commit()
		flash("Menu item has been deleted!")
		return redirect(url_for('catalogMain'))
	else:	
		return render_template('itemdelete.html', item=itemToDelete) 

#Provide JSON endpoint
@app.route('/catalog/<int:category_id>/JSON')
def categoryToJson(category_id):
	category = session.query(Category).filter_by(id = category_id).one()
	items = session.query(CategoryItem).filter_by(category_id = category_id).all()
	return jsonify(CategoryItems=[i.serialize for i in items])

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)