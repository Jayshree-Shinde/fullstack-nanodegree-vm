#!/usr/bin/python
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from Project2_databaseSetup import Base, Category, Item, Users
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from flask import Flask, render_template, request, \
    redirect, jsonify, url_for, flash

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Sports Catalog App"


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('logi.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    '''This function is used to create a google plus login'''
    
    #Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    #Obtain authorization code
    code = request.data

    try:
        #Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
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
        return response

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
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is \
                                            already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception:
        return None


@app.route('/gdisconnect')
def gdisconnect():
    '''This function is used to revoke a current user's token and reset their login_session'''
    access_token = login_session.get('access_token')
    if access_token is None:
        print ('Access Token is None')
        response = make_response(json.dumps('Current user \
                                            not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print ('In gdisconnect access token is %s'), access_token
    print ('User name is:')
    print (login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print ('result is ')
    print (result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for \
                                            given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view users
@app.route('/users/JSON')
def userJSON():
    users = session.query(User).all()
    return jsonify(User=[u.serialize for u in users])


# JSON APIs to view all categories
@app.route('/categories/json')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(Categories=[c.serialize for c in categories])


# JSON APIs to view all items of a category
@app.route('/catalog/<category_name>/items/JSON')
def categoryJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(Items=[i.serialize for i in items])


# JSON APIs to view arbitary items
@app.route('/restaurant/<category_name>/items/<item_name>/JSON')
def itemJSON(category_id, menu_id):
    Item = session.query(Item).filter_by(id=menu_id).one()
    return jsonify(Item=Item.serialize)


# Connect to Database and create database session
engine = create_engine('sqlite:///catalogapp.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Show all categories
@app.route('/')
@app.route('/catalog/')
def showCategories():
    category = session.query(Category)
    items = session.query(Item)
    return render_template('categoryTemplate.html',
                           category=category, items=items)


# Show all items in a selected category
@app.route('/catalog/<category_name>/items')
def showItems(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_id=category.id).all()
    return render_template('itemTemplate.html', items=items, category=category)


# Show description of the selected item
@app.route('/catalog/<category_name>/<item_name>')
def showItemInfo(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = (session.query(Item).filter_by(name=item_name,
             category=category).one())
    return render_template('itemDecriptionTemplate.html',
                           items=items, category=category)


# Add new item
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newItem(category_id):
    user_id = login_session['user_id']
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        description = request.form['description']
        category = session.query(Category).filter_by(id=category_id).one()
        newItem = Item(id=id, name=name, description=description,
                       category=category, user_id=user_id)
        session.add(newItem)
        session.commit()
        flash('New Item %s Successfully Created' % newItem.name)
        return redirect(url_for('showItems', category_id=category_id))
    else:
        return render_template('newItemTemplate.html', category_id=category_id)

    return render_template('newItemTemplate.html', category_id=category_id)


# Edit an item
@app.route('/catalog/<item_name>/edit', methods=['GET', 'POST'])
def editItem(category_id, item_id):
    user_id = login_session['user_id']
    if 'username' not in login_session:
        return redirect('/login')

    catalog = session.query(Cestaurant).filter_by(id=category_id).one()
    itemToBeEdited = session.query(Item).filter_by(id=item_id).one()

    if itemToBeEdited.user_id != login_session['user_id']:
        flash('Item cannot be edited by you!!!')

    if request.method == 'POST':
        if request.form['name']:
            itemToBeEdited.name = request.form['name']
        if request.form['description']:
            itemToBeEdited.description = request.form['description']
            session.add(itemToBeEdited)
            session.commit()
            flash('Item Successfully Edited')
            return redirect(url_for('showItems', category_id=category_id))
        else:
            return render_template('editItem.html',
                                   restaurant_id=restaurant_id,
                                   menu_id=menu_id, item=editedItem)


#Delete an item
@app.route('/catalog/<item_name>/delete', methods=['GET', 'POST'])
def deleteMenuItem(category_id, item_id):
    user_id = login_session['user_id']
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Catalog).filter_by(id=category_id).one()
    itemToDeleted = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(itemToDeleted)
        session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for('showItems', category_id=category_id))
    else:
        return render_template('deleteItem.html', item=itemToDelete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
