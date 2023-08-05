import locale

import requests
from flask import Flask, current_app, g
from flask.ext.principal import identity_loaded
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf.csrf import CsrfProtect

from .sqlstats import DB_STATS


__version__ = '0.4.9'


requests_session = requests.Session()


# Set default locale
locale.setlocale(locale.LC_ALL, '')


db = SQLAlchemy()

# Ensure models are declared
from . import models
from .auth import models


csrf = CsrfProtect()


def create_app(**kwargs):
    app = Flask('evesrp', **kwargs)
    app.config.from_object('evesrp.default_config')

    # Register SQLAlchemy monitoring before the DB is connected
    app.before_request(sqlalchemy_before)

    db.init_app(app)

    from .views.login import login_manager
    login_manager.init_app(app)

    from .auth import principal
    principal.init_app(app)

    csrf.init_app(app)

    from .views import index, divisions, login, requests, api
    app.add_url_rule(rule='/', view_func=index)
    app.register_blueprint(divisions.blueprint, url_prefix='/divisions')
    app.register_blueprint(login.blueprint)
    app.register_blueprint(requests.blueprint)
    app.register_blueprint(api.api, url_prefix='/api')
    app.register_blueprint(api.filters, url_prefix='/api/filter')

    from .json import SRPEncoder
    app.json_encoder=SRPEncoder

    from .auth import load_user_permissions
    identity_loaded.connect(load_user_permissions, app)

    app.before_first_request(_copy_config_to_authmethods)
    app.before_first_request(_config_requests_session)
    app.before_first_request(_config_killmails)
    app.before_first_request(_copy_url_converter_config)

    return app


# SQLAlchemy performance logging
def sqlalchemy_before():
    DB_STATS.clear()
    g.DB_STATS = DB_STATS


# Auth setup
def _copy_config_to_authmethods():
    current_app.auth_methods = current_app.config['AUTH_METHODS']


# Request detail URL setup
def _copy_url_converter_config():
    current_app.ship_urls = {}
    ship_transformers = current_app.config.get('SRP_SHIP_URL_TRANSFORMERS')
    if ship_transformers is not None:
        for transformer in ship_transformers:
            current_app.ship_urls[transformer.name] = transformer
    current_app.pilot_urls = {}
    pilot_transformers = current_app.config.get('SRP_PILOT_URL_TRANSFORMERS')
    if pilot_transformers is not None:
        for transformer in pilot_transformers:
            current_app.pilot_urls[transformer.name] = transformer


# Requests session setup
def _config_requests_session():
    try:
        ua_string = current_app.config['USER_AGENT_STRING']
    except KeyError as outer_exc:
        try:
            ua_string = 'EVE-SRP/0.1 ({})'.format(
                    current_app.config['USER_AGENT_EMAIL'])
        except KeyError as inner_exc:
            raise inner_exc from outer_exc
    requests_session.headers.update({'User-Agent': ua_string})
    current_app.user_agent = ua_string


# Killmail verification
def _config_killmails():
    current_app.killmail_sources = current_app.config['KILLMAIL_SOURCES']
