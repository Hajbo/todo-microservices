from app import db
from passlib.hash import pbkdf2_sha256 as sha256

class UserModel(db.Model):
    """
    User Model Class
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    """
    Save user details in Database
    """
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    """
    Find user by username
    """
    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    """
    return all the user data in json form available in DB
    """
    @classmethod
    def return_all(cls):
        def to_json(x):
            return {"username": x.username, "password": x.password}
        return {"users": [to_json(user) for user in UserModel.query.all()]}

    """
    Delete user data
    """
    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {"message": f"{num_rows_deleted} row(s) deleted"}
        except:
            return {"message": "Something went wrong"}

    """
    generate hash from password by encryption using sha256
    """
    @staticmethod
    def generate_hash(password):

        return sha256.hash(password)

    """
    Verify hash and password
    """
    @staticmethod
    def verify_hash(password, hash_):
        return sha256.verify(password, hash_)

    """
    Delete user by UUID
    """
    @classmethod
    def delete_by_uuid(cls, uuid):
        try:
            cls.query.filter_by(uuid=uuid).delete()
            db.session.commit()
            return {"message": f"User with uuid {uuid} deleted"}
        except Exception as e:
            return {"message": "Something went wrong: " + str(e)}
