#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class IndexArticle(Resource):
    
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            article_json = jsonify(article.to_dict())

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401
    
#  creating a Login resource
class Login(Resource):
    #  a post method  to get the username and set the user to a session 
    def post(self):
        # querying and filtering by the user by the username since there is no password yet
        user = User.query.filter(User.username == request.get_json()["username"]).first()

        # setting the session using the id
        session["user_id"] = user.id
        #  creating and returning a  response
        response_dict = user.to_dict()
        response = make_response(response_dict,200)
        return response
    pass

# add the Login resource to the api
api.add_resource(Login, "/login")

# creating a Logout resource
class Logout(Resource):
    # a delete method to clear out the user once they are logged out
    def delete(self):
        # setting the session hash to none 
        session["user_id"] = None
        #  creating and returning a  response
        response_body = {"msg": "No data: 204(No Content)"}
        response = make_response(response_body,204)
        return response
    pass

# adding the Logout resource to the api
api.add_resource(Logout, "/logout")

# creating a CheckSession resource 
class CheckSession(Resource):
    #  a get method that retrieves the user_id from the session
    def get(self):
        
        #  using query and filter to get the session using the users id
        user = User.query.filter(User.id == session.get("user_id")).first()

        #  if the session has a user id return the user else return an error
        if user:
            #  creating and returning a  response
            response_dict = user.to_dict()
            response = make_response(response_dict,200)
            return response
        else:
            #  creating and returning a  response
            response_body = {}
            response = make_response(response_body,401)
            return response

    pass

# add the CheckSession resource to the api
api.add_resource(CheckSession, "/check_session")

api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
