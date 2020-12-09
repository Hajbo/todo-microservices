from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from rabbit import run_consumers
from jaeger_client import Config
from flask_opentracing import FlaskTracer

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
        service_name='user-service',
        validate=True,
    )
  return config.initialize_tracer() # also sets opentracing.tracer

flask_tracer = FlaskTracer(initialize_tracer, True, app)
app.config["FLASK_TRACER"] = flask_tracer

# Object of Api class
api = Api(app)

# Application Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://todoapp:todoapp@postgresdb:5432/users"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "ThisIsHardestThing"


# SqlAlchemy object
db = SQLAlchemy(app)

# Generating tables before first request is fetched
@app.before_first_request
def setup_app():
    db.create_all()
    # Start RabbitMQ consumer
    run_consumers()



# Importing resources
import resources

# Api Endpoints
api.add_resource(resources.AllUsers, "/users")
api.add_resource(resources.UserByUsername, "/users/username")
api.add_resource(resources.UserByUUID, "/users/uuid")
