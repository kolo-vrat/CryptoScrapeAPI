from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(*args, **kwargs):
    env = kwargs["env"]
    app = Flask(__name__)
    app.config.from_object(f"conf.{env}")
    app.json.sort_keys = False
    db.init_app(app)

    with app.app_context():
        db.Model.metadata.reflect(db.engine)

    return app
