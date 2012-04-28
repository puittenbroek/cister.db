from pyramid.config import Configurator
from sqlalchemy import engine_from_config
import pyramid_zcml
from cister.db.models.cister import initialize_sql
from pyramid.session import UnencryptedCookieSessionFactoryConfig

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)

    session_factory = UnencryptedCookieSessionFactoryConfig('topsecret', cookie_secure=True)
    config = Configurator(settings=settings,
                          session_factory=session_factory,
                          root_factory='cister.db.models.cister.RootFactory')

    config.add_static_view('static', 'cister.db:static', cache_max_age=3600)


    config.include(pyramid_zcml)
    zcml_file = 'configure.zcml'
    config.load_zcml(zcml_file)

    return config.make_wsgi_app()

