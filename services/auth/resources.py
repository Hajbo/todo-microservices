from flask import current_app
from flask_restful import Resource, reqparse
import uuid
import opentracing
from models import UserModel
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt,
    get_jti,
)
import pdb
from rabbit import emit_user_creation
from datetime import timedelta


ACCESS_EXPIRES = timedelta(minutes=15)
REFRESH_EXPIRES = timedelta(days=30)


parser = reqparse.RequestParser()
parser.add_argument("username", help="username cannot be blank", required=True)
parser.add_argument("password", help="password cannot be blank", required=True)


class UserRegistration(Resource):
    """
    User Registration Api
    """

    def post(self):
        flask_tracer = current_app.config.get("FLASK_TRACER")
        parent_span = flask_tracer.get_span()

        revoked_store = current_app.config.get("REVOKED_STORE")

        data = parser.parse_args()
        username = data["username"]
        
        with opentracing.tracer.start_span('user-register', child_of=parent_span) as span:
            span.set_tag("username", username)
        
        if UserModel.find_by_username(username):
            return {"message": f"User {username} already exists"}

        new_user = UserModel(
            uuid=str(uuid.uuid4()), username=username, password=UserModel.generate_hash(data["password"])
        )

        try:
            new_user.save_to_db()
            access_token = create_access_token(identity=username)
            refresh_token = create_refresh_token(identity=username)

            access_jti = get_jti(encoded_token=access_token)
            refresh_jti = get_jti(encoded_token=refresh_token)
            revoked_store.set(access_jti, "false", ACCESS_EXPIRES * 1.2)
            revoked_store.set(refresh_jti, "false", REFRESH_EXPIRES * 1.2)

            try:
                emit_user_creation(new_user.username, new_user.uuid)
            except Exception as e:
                return {"message": "Emitting error: " + str(e)}, 500

            return {
                "message": f"User {username} was created",
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        except Exception as e:
            return {"message": "Something went wrong: " + str(e)}, 500


class UserLogin(Resource):
    """
    User Login Api
    """
    def post(self):
        data = parser.parse_args()
        username = data["username"]
        current_user = UserModel.find_by_username(username)

        revoked_store = current_app.config.get("REVOKED_STORE")

        if not current_user:
            return {"message": f"User {username} doesn't exist"}

        if UserModel.verify_hash(data["password"], current_user.password):
            access_token = create_access_token(identity=username)
            refresh_token = create_refresh_token(identity=username)

            access_jti = get_jti(encoded_token=access_token)
            refresh_jti = get_jti(encoded_token=refresh_token)
            revoked_store.set(access_jti, "false", ACCESS_EXPIRES * 1.2)
            revoked_store.set(refresh_jti, "false", REFRESH_EXPIRES * 1.2)
            return {
                "message": f"Logged in as {username}",
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        else:
            return {"message": "Wrong credentials"}


class UserLogoutAccess(Resource):
    """
    User Logout Api
    """
    @jwt_required
    def post(self):
        jti = get_raw_jwt()["jti"]
        revoked_store = current_app.config.get("REVOKED_STORE")
        try:
            revoked_store.set(jti, "true", ACCESS_EXPIRES * 1.2)
            return {"message": "Access token has been revoked"}
        except:
            return {"message": "Something went wrong"}, 500


class UserLogoutRefresh(Resource):
    """
    User Logout Refresh Api
    """
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()["jti"]
        revoked_store = current_app.config.get("REVOKED_STORE")
        try:
            revoked_store.set(jti, "true", ACCESS_EXPIRES * 1.2)
            pdb.set_trace()
            return {"message": "Refresh token has been revoked"}
        except:
            return {"message": "Something went wrong"}, 500


class TokenRefresh(Resource):
    """
    Token Refresh Api
    """
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        
        revoked_store = current_app.config.get("REVOKED_STORE")
        access_jti = get_jti(encoded_token=access_token)
        revoked_store.set(access_jti, "false", ACCESS_EXPIRES * 1.2)
        return {"access_token": access_token}


class AllUsers(Resource):
    def get(self):
        """
        return all user api
        """
        return UserModel.return_all()

    def delete(self):
        """
        delete all user api
        """
        return UserModel.delete_all()


class VerifyResource(Resource):
    """
    Secrest Resource Api
    You can create crud operation in this way
    """
    @jwt_required
    def get(self):
        return {"answer": "Verified"}
