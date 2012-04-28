from pyramid.renderers import get_renderer
from cister.db import helpers
from datetime import datetime

def add_base_template(event):
    main = get_renderer('templates/main.pt').implementation()
    generic_macros = get_renderer('templates/macro/generic_macros.pt').implementation()
    base_search = get_renderer('templates/base/search.pt').implementation()
    event.update({'main': main})
    event.update({'generic_macros': generic_macros})
    event.update({'base_search': base_search})

def add_renderer_globals(event):
   event['h'] = helpers
   event['default_search'] = 'Refine your search'
   event['datetime'] = datetime
