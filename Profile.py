import psycopg2 as dbapi2
from database import database
import datetime
from user import *
from flask_login import  current_user

class Profile():
    def __init__(cls, id, username, name, surname, email):
        cls.id = id
        cls.username = username
        cls.name = name
        cls.surname = surname
        cls.email = email

    class ProfileRecipeInfo():
        def __init__(cls, id, name, description, procedure, ingredient, amount):
            cls.id = id
            cls.name = name
            cls.description = description
            cls.procedure = procedure
            cls.ingredient = ingredient
            cls.amount = amount


    @classmethod
    def get_userInfo(cls,username):
        userInfo = None
        with dbapi2.connect(database.config) as connection:
            cursor = connection.cursor()
            query = """SELECT Name,Surname,Mail,CreateDate,LastLoginDate,Username,UserID FROM UserInfo WHERE Username ='%s'""" %username

            try:
                cursor.execute(query)

            except dbapi2.Error:
                print("rollback ERROR")
                connection.rollback()
            else:
                print("ERROR")
                userInfo = cursor.fetchall()
                connection.commit()

            cursor.close()
        return userInfo

    @classmethod
    def update_userInfo(cls, userID,newUserInfo):
        with dbapi2.connect(database.config) as connection:
            cursor = connection.cursor()

            try:
                if newUserInfo[0] != '':
                    query = """UPDATE UserInfo SET Name = '%s' WHERE userID = %d""" % (newUserInfo[0],int(userID))
                    cursor.execute(query)
                if newUserInfo[1] != '':
                    query = """UPDATE UserInfo SET Surname = '%s' WHERE userID = %d""" % (newUserInfo[1],int(userID))
                    cursor.execute(query)
                if newUserInfo[2] != '':
                    query = """UPDATE UserInfo SET Mail = '%s' WHERE userID = %d""" % (newUserInfo[2],int(userID))
                    cursor.execute(query)
                if newUserInfo[3] != '':
                    query = """UPDATE UserInfo SET Username = '%s' WHERE userID = %d""" % (newUserInfo[3],int(userID))
                    cursor.execute(query)
                if newUserInfo[4] != '':
                    hashp = pwd_context.encrypt(newUserInfo[4])
                    query = """UPDATE UserInfo SET Password = '%s' WHERE userID = %d""" % (hashp,int(userID))
                    cursor.execute(query)

            except dbapi2.Error:
                connection.rollback()
            else:
                connection.commit()
                cursor.close()
            return True

    @classmethod
    def whatShouldIBrewToday(self):

        with dbapi2.connect(database.config) as connection:
            cursor = connection.cursor()
            recipeInfo = None
            userId = current_user.id
            print("current user id",userId)
            #query = """SELECT k.name, k.description, k.procedure, z.name, l.amount  FROM RecipeInfo k, RecipeMap l, IngredientMap x, RateCommentInfo y, IngredientParameter z
            #            WHERE z.ID = l.IngredientID and k.RecipeID = l.RecipeID and y.RecipeID = k.RecipeID  and x.UserID = %d and (l.IngredientID = x.IngredientID and x.Amount > l.Amount)
            #            """ %(userId)  #ORDER BY AVG(Rate) DESC and (l.IngredientID = x.IngredientID and x.Amount > l.Amount)
            query = """SELECT z.Name, z.description, z.procedure, k.name, y.amount 
                                    FROM IngredientMap as x, RecipeMap as y, RecipeInfo as z, IngredientParameter as k
                                      WHERE k.ID = x.IngredientID and z.ID = y.RecipeID and y.IngredientID = k.ID and x.IngredientID = y.IngredientID and x.UserID = %d 
                                      """ % (userId)
            try:
                cursor.execute(query)

            except dbapi2.Error:
                connection.rollback()
            else:
                recipeInfo = cursor.fetchall()
                connection.commit()

            cursor.close()
        return recipeInfo

    @classmethod
    def getUserRecipe(self):
        with dbapi2.connect(database.config) as connection:
            cursor = connection.cursor()
            userId = current_user.id
            print(userId)
            recipeInfo = None
            query = """SELECT k.RecipeID, k.name, k.description, k.procedure, m.name, l.amount
                        FROM RecipeInfo as k, RecipeMap as l, IngredientParameter as m 
                         WHERE k.RecipeID = l.RecipeID  AND l.IngredientID = m.ID and k.userID = %d
                         """ % (userId)
            try:
                cursor.execute(query)

            except dbapi2.Error:
                print("ROLLBACK ERROR")
                connection.rollback()
            else:
                recipeInfo = cursor.fetchall()
                connection.commit()
            list = [[]for a in range(50)]
            j = 0
            k = 0
            lastID = 0
            for i in recipeInfo:
                print(k)
                if j == 0:
                    list[0].append(i)
                    lastID = i[0]
                    j = 1
                else:
                    if i[0] == lastID:
                        list[k].append(i)
                    else:
                        k = k + 1
                        list[k].append(i)
                        lastID = i[0]
            cursor.close()
        return list

    @classmethod
    def deleteRecipe(self, recipeID):
        with dbapi2.connect(database.config) as connection:
            cursor = connection.cursor()
            query = "DELETE FROM RECIPEMAP WHERE recipeID= '%d'" % (recipeID)
            try:
                cursor.execute(query)
            except dbapi2.Error:

                print("RollBack Error")
            else:
                connection.commit()
            query = "DELETE FROM RECIPEINFO WHERE recipeID= '%d'" % (recipeID)

            try:
                cursor.execute(query)
            except dbapi2.Error:
                print("ROLLBACK ERROR")
                connection.rollback()
            else:
                connection.commit()
            cursor.close()
            return

    @classmethod
    def recipeApply(self, recipeID):
        with dbapi2.connect(database.config) as connection:
            cursor = connection.cursor()
            query = """SELECT IngredientID, Amount FROM RecipeMap WHERE RecipeID = %d""" %(recipeID)
            try:
                cursor.execute(query)

            except dbapi2.Error:
                connection.rollback()
            else:
                recipeIngredientInfo = cursor.fetchall()
                connection.commit()

            userId = current_user.id
            query = """SELECT IngredientID, Amount FROM IngredientMap WHERE UserID = %d""" %(userId)

            try:
                cursor.execute(query)

            except dbapi2.Error:
                connection.rollback()
            else:
                userIngredientInfo = cursor.fetchall()
                connection.commit()


        ctrl = 0
        for i in recipeIngredientInfo:
            for j in userIngredientInfo:
                if i[0] == j[0]:
                    if i[1] > j[1]:
                        ctrl = 1

        if ctrl == 1:
            return "Not enough ingredients"
        else:
            for i in recipeIngredientInfo:
                for j in userIngredientInfo:
                    if i[0] == j[0]:
                        query = """UPDATE IngredientMap SET Amount = %s WHERE IngredientID = %s"""

                        try:
                            cursor.execute(query, (j[1]-i[1],i[0]))

                        except dbapi2.Error:
                            connection.rollback()
                        else:
                            connection.commit()
            cursor.close()
            return "Successful"