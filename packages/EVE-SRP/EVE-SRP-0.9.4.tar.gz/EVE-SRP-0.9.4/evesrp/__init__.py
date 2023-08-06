from __future__ import absolute_import
import locale
import os
import requests
from flask import Flask, current_app, g
from flask.ext import sqlalchemy
from flask.ext.wtf.csrf import CsrfProtect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData


db = sqlalchemy.SQLAlchemy()
# Patch Flask-SQLAlchemy to use a custom Metadata instance with a naming scheme
# for constraints.
def _patch_metadata():
    naming_convention = {
        'fk': ('fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s'
                '_%(referred_column_0_name)s'),
        'pk': 'pk_%(table_name)s',
        'ix': 'ix_%(table_name)s_%(column_0_name)s',
        'ck': 'ck_%(table_name)s_%(constraint_name)s',
        'uq': 'uq_%(table_name)s_%(column_0_name)s',
    }
    metadata = MetaData(naming_convention=naming_convention)
    base = declarative_base(cls=sqlalchemy.Model, name='Model',
                            metaclass=sqlalchemy._BoundDeclarativeMeta,
                            metadata=metadata)
    base.query = sqlalchemy._QueryProperty(db)
    db.Model = base
_patch_metadata()


from .util import DB_STATS, AcceptRequest


__version__ = u'0.9.4'


requests_session = requests.Session()


# Set default locale
locale.setlocale(locale.LC_ALL, '')


csrf = CsrfProtect()


# Ensure models are declared
from . import models
from .auth import models as auth_models


def create_app(config=None, **kwargs):
    app = Flask('evesrp', **kwargs)
    app.request_class = AcceptRequest
    app.config.from_object('evesrp.default_config')
    if config is not None:
        app.config.from_pyfile(config)
    if app.config['SECRET_KEY'] is None and 'SECRET_KEY' in os.environ:
        app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

    # Register SQLAlchemy monitoring before the DB is connected
    app.before_request(sqlalchemy_before)

    db.init_app(app)

    from .views.login import login_manager
    login_manager.init_app(app)

    before_csrf = list(app.before_request_funcs[None])
    csrf.init_app(app)
    # Remove the context processor that checks CSRF values. All it is used for
    # is the template function.
    app.before_request_funcs[None] = before_csrf

    from .views import index, error_page, divisions, login, requests, api
    app.add_url_rule(rule=u'/', view_func=index)
    for error_code in (400, 403, 404, 500):
        app.register_error_handler(error_code, error_page)
    app.register_blueprint(divisions.blueprint, url_prefix='/division')
    app.register_blueprint(login.blueprint)
    app.register_blueprint(requests.blueprint, url_prefix='/request')
    app.register_blueprint(api.api, url_prefix='/api')
    app.register_blueprint(api.filters, url_prefix='/api/filter')

    from .views import request_count
    app.add_template_global(request_count)

    from .json import SRPEncoder
    app.json_encoder=SRPEncoder

    app.before_first_request(_copy_config_to_authmethods)
    app.before_first_request(_config_requests_session)
    app.before_first_request(_config_killmails)
    app.before_first_request(_copy_url_converter_config)

    # Configure the Jinja context
    # Inject variables into the context
    from .auth import PermissionType
    @app.context_processor
    def inject_enums():
        return {
            'ActionType': models.ActionType,
            'PermissionType': PermissionType,
            'app_version': __version__,
            'site_name': app.config['SRP_SITE_NAME'],
            'url_for_page': requests.url_for_page,
        }
    # Auto-trim whitespace
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    return app


# SQLAlchemy performance logging
def sqlalchemy_before():
    if DB_STATS.total_queries > 0:
        current_app.logger.debug(u"{} queries in {} ms.".format(
                DB_STATS.total_queries,
                round(DB_STATS.total_time * 1000, 3)))
    DB_STATS.clear()
    g.DB_STATS = DB_STATS


# Auth setup
def _copy_config_to_authmethods():
    current_app.auth_methods = current_app.config['SRP_AUTH_METHODS']


# Request detail URL setup
def _copy_url_converter_config():
    url_transformers = {}
    for config_key, config_value in current_app.config.items():
        if config_value is None:
            continue
        index = config_key.rfind('_URL_TRANSFORMERS')
        if not config_key.endswith('_URL_TRANSFORMERS')\
                or not config_key.startswith('SRP_'):
            continue
        attribute = config_key.replace('SRP_', '', 1)
        attribute = attribute.replace('_URL_TRANSFORMERS', '', 1)
        attribute = attribute.lower()
        url_transformers[attribute] = {t.name:t for t in config_value}
    current_app.url_transformers = url_transformers
    # temporary compatibility
    current_app.ship_urls = url_transformers.get('ship_type', None)
    current_app.pilot_urls = url_transformers.get('pilot', None)


# Requests session setup
def _config_requests_session():
    try:
        ua_string = current_app.config['SRP_USER_AGENT_STRING']
    except KeyError as outer_exc:
        try:
            ua_string = 'EVE-SRP/{version} ({email})'.format(
                    email=current_app.config['SRP_USER_AGENT_EMAIL'],
                    version=__version__)
        except KeyError as inner_exc:
            raise inner_exc
    requests_session.headers.update({'User-Agent': ua_string})
    current_app.user_agent = ua_string


# Killmail verification
def _config_killmails():
    current_app.killmail_sources = current_app.config['SRP_KILLMAIL_SOURCES']
