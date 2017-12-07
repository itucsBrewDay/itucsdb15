from flask import Blueprint
from database import database
from user import *
import datetime
from passlib.apps import custom_app_context as pwd_context
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask_login import login_user, current_user, login_required, logout_user

from user import UserLogin
from Recipe import Recipe
from Profile import Profile
site = Blueprint('site',__name__)

@site.route('/initdb')
def initialize_database():
	loremipsum = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam et rutrum sem, nec scelerisque ex. Ut mollis, quam vitae eleifend ornare, sapien est semper magna, sed fermentum diam neque ac est. Praesent at cursus lorem. Ut metus leo, laoreet non bibendum in, efficitur nec nisi. Cras lobortis ut quam nec volutpat. Fusce massa lectus, varius eget magna eget, egestas lacinia sapien. Morbi eget tellus orci. Nullam egestas velit urna, eget porta dui vehicula nec. Integer aliquet, neque et viverra sagittis, turpis lorem facilisis nisl, vitae consectetur magna erat at orci. Praesent fermentum justo erat. Duis tincidunt, eros nec ullamcorper molestie, odio magna viverra urna, quis tincidunt tortor nisl id nisl. Sed ut erat sit amet quam ultrices posuere.'
	database.create_tables()
	database.init_db()
	UserLogin.init_admin()
	for r in range(1, 19):
		Recipe.add(UserLogin.select_user("admin"), "Recipe%r" % r, loremipsum, "Procedure of Recipe%r" % r)

	return redirect(url_for('site.home_page'))

@site.route('/')
def home_page():
	recipes = Recipe.getall()
	print("Current user: ",current_user.is_authenticated)

	return render_template('home.html', recipes=recipes)

@site.route('/logout')
@login_required
def logout():
	print("Logout user:", current_user.username)
	logout_user()
	return redirect(url_for('site.home_page'))

@site.route('/login', methods=['GET', 'POST'])
def login_page():
	if request.method == 'GET':

		return render_template('login.html')
	else:
		user = UserLogin.select_user(request.form['username'])
		if user and user != -1:
			if pwd_context.verify(request.form['password'], user.password):
				UserLogin.setLastLoginDate(user)
				login_user(user)
				print("Current user:",current_user.username)
				return redirect(url_for('site.home_page'))


@site.route('/register', methods=['GET', 'POST'])
def register_page():
	if request.method == 'GET':
		return render_template('register.html')
	else:
		print("register add")
		name = request.form['name']
		surname =  request.form['surname']
		email = request.form['email']
		username = request.form['username']
		password = request.form['password']
		confirm = request.form['confirm']
		if password == confirm:
			UserLogin.add_user(name, surname, email, username , password)
		else:
			pass  # will be implemented later

		return redirect(url_for('site.login_page'))

@site.route('/search_recipe', methods=['GET', 'POST'])
@login_required
def search_recipe():
	print("Current user:", current_user.username)
	if request.method == 'GET':
		return render_template('search_recipe.html')
	else:
		return render_template('search_recipe.html', recipes=Recipe.get_like(request.form['search']))

@site.route('/profile', methods=['GET', 'POST'])
@login_required
def profile_page():
    if request.method == 'GET':
        userInfo = Profile.get_userInfo(current_user.username)
        print(userInfo)
        return render_template('profile.html', userInfo=userInfo)
    else:
        print("heyy")
        return render_template('profile_add.html')


@site.route('/profile/edit/<int:userID>/', methods=['GET', 'POST'])
@login_required
def profile_edit(userID):
	print("Current user:", current_user.username)
	if request.method == 'GET':
		userInfo = Profile.get_userInfo(current_user.username)
		print(userInfo)
		return render_template('profile_edit.html',userInfo=userInfo)
	else:
		newUserInfo = []
		print("Update Profile")
		newUserInfo.append(request.form['name'])
		newUserInfo.append(request.form['surname'])
		newUserInfo.append(request.form['email'])
		newUserInfo.append(request.form['username'])
		newUserInfo.append(request.form['password'])

		Profile.update_userInfo(userID,newUserInfo= newUserInfo)
		return redirect(url_for('site.profile_page'))

@site.route('/profile/add', methods=['GET', 'POST'])
@login_required
def profile_recipe_add():
    with dbapi2.connect(database.config) as connection:
        cursor = connection.cursor()

    if request.method == 'GET':
        return render_template('profile_add.html')
        #query = """ SELECT ID,NAME FROM PARAMETERTYPE WHERE ID='%d'"""% TYPE
        #cursor.execute(query)
        #typeName = cursor.fetchone()


        #return render_template('parameter_add.html', user=current_user.username, parameterType=typeName)
    else:
        #parameterName = request.form['parameterType']

        #query = "INSERT INTO PARAMETERS(TYPEID,NAME) VALUES('%d', '%s')" % (TYPE, parameterName)
        #cursor.execute(query)

        #connection.commit()

        return redirect(url_for('site.profile_page'))


        #parameterName = request.form['parameterType']
#
#
        #query = "INSERT INTO PARAMETERS(TYPEID,NAME) VALUES('%d', '%s')" % (TYPE,parameterName)
        #cursor.execute(query)
#
        #connection.commit()
#
        #return redirect(url_for('site.parameters_page'))