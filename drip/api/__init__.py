import config
import pkgutil
import importlib
from flask import Flask, Blueprint
from drip.datastore import db


def create_app(package_name=__name__, package_path=__path__, has_blueprints=True, **config_overrides):
    app = Flask(package_name, static_url_path='')
    app.config.from_object(config)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Apply overrides.
    app.config.update(config_overrides)

    # Initialize the database and declarative Base class.
    db.init_app(app)

    # Create the database tables.
    # Flask-SQLAlchemy needs to know which
    # app context to create the tables in.
    with app.app_context():
        db.create_all()

    # Register blueprints.
    if has_blueprints:
        register_blueprints(app, package_name, package_path)

    return app


def register_blueprints(app, package_name, package_path):
    """register all Blueprint instances on the specified
    Flask application found in all modules for the specified package"""
    results = []
    for _, name, _ in pkgutil.iter_modules(package_path):
        m = importlib.import_module('%s.%s' % (package_name, name))
        for item in dir(m):
            item = getattr(m, item)
            if isinstance(item, Blueprint):
                app.register_blueprint(item)
            results.append(item)
    return results
