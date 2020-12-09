from flask import request
from flask_restful import Resource, reqparse
from models import UserModel
from rabbit import emit_user_deletion


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


class UserByUsername(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("username")
        args = parser.parse_args()
        x = UserModel.find_by_username(args.get("username"))
        if x:
            return {"username": x.username, "uuid": x.uuid}
        return {"message": "User not found by username " + args.get("username")}, 404


class UserByUUID(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("uuid")
        args = parser.parse_args()
        x = UserModel.find_by_uuid(args.get("uuid"))
        if x:
            return {"username": x.username, "uuid": x.uuid}
        return {"message": "User not found by uuid " + args.get("uuid")}, 404

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument("uuid")
        args = parser.parse_args()

        auth_header = request.headers.get('Authorization')
        jwt = auth_header.split(' ')[1]
        try:
            emit_user_deletion(args.get("uuid"), jwt)
            UserModel.delete_by_uuid(args.get("uuid"))
        except Exception as e:
            return {"message": "Emitting error: " + str(e)}, 500
        return {"message": "User deleted by UUID " + args.get("uuid")}, 200
