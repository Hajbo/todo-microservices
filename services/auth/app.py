from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from jaeger_client import Config
from flask_opentracing import FlaskTracer
import redis
from datetime import timedelta
import secrets
from rabbit import run_consumers

# Making Flask Application
app = Flask(__name__)

def initialize_tracer():
  config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'local_agent': {
                'reporting_host': 'jaeger',
                'reporting_port': '6831',
            },
            'logging': True,
        },
        service_name='auth-service',
        validate=True,
    )
  return config.initialize_tracer() # also sets opentracing.tracer

flask_tracer = FlaskTracer(initialize_tracer, True, app)
app.config["FLASK_TRACER"] = flask_tracer

# Object of Api class
api = Api(app)

# Application Configuration
ACCESS_EXPIRES = timedelta(minutes=15)
REFRESH_EXPIRES = timedelta(days=30)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = REFRESH_EXPIRES
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@mysqldb:3306/authdb"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = secrets.token_hex(32)
app.config["JWT_SECRET_KEY"] = secrets.token_hex(32)
app.config["JWT_BLACKLIST_ENABLED"] = True
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"]

# SqlAlchemy object
db = SQLAlchemy(app)

# JwtManager object
jwt = JWTManager(app)

# Generating tables before first request is fetched
@app.before_first_request
def create_tables():
    db.create_all()
    # Start RabbitMQ consumers
    run_consumers()

# Setup our redis connection for storing the blacklisted tokens
revoked_store = redis.StrictRedis(
    host="redis", port=6379, db=0, decode_responses=True
)
app.config["REVOKED_STORE"] = revoked_store

# Checking that token is in blacklist or not
@jwt.token_in_blacklist_loader
def check_if_token_is_revoked(decrypted_token):
    jti = decrypted_token["jti"]
    entry = revoked_store.get(jti)
    if entry is None:
        return True
    return entry == "true"


# Importing models and resources
import models, resources

# Api Endpoints
api.add_resource(resources.UserRegistration, "/api/registration")
api.add_resource(resources.UserLogin, "/api/login")
api.add_resource(resources.UserLogoutAccess, "/api/logout/access")
api.add_resource(resources.UserLogoutRefresh, "/api/logout/refresh")
api.add_resource(resources.TokenRefresh, "/api/token/refresh")
api.add_resource(resources.AllUsers, "/api/users")
api.add_resource(resources.VerifyResource, "/api/verify")
