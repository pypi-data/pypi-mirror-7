import logging
from pyramid.view import view_config

from ringo.views.base import list_, create_, update_, read_, delete_,\
export_, import_
from ringo.views.json import (
    list_   as json_list,
    create_ as json_create,
    update_ as json_update,
    read_   as json_read,
    delete_ as json_delete
    )
from ringo.lib.helpers import import_model
Role = import_model('ringo.model.user.Role')

log = logging.getLogger(__name__)

###########################################################################
#                               HTML VIEWS                                #
###########################################################################

@view_config(route_name=Role.get_action_routename('list'),
             renderer='/default/list.mako',
             permission='list')
def list(request):
    return list_(Role, request)


@view_config(route_name=Role.get_action_routename('create'),
             renderer='/default/create.mako',
             permission='create')
def create(request):
    return create_(Role, request)


@view_config(route_name=Role.get_action_routename('update'),
             renderer='/default/update.mako',
             permission='update')
def update(request):
    return update_(Role, request)


@view_config(route_name=Role.get_action_routename('read'),
             renderer='/default/read.mako',
             permission='read')
def read(request):
    return read_(Role, request)


@view_config(route_name=Role.get_action_routename('delete'),
             renderer='/default/confirm.mako',
             permission='delete')
def delete(request):
    return delete_(Role, request)

@view_config(route_name=Role.get_action_routename('export'),
             renderer='/default/export.mako',
             permission='export')
def export(request):
    return export_(Role, request)

@view_config(route_name=Role.get_action_routename('import'),
             renderer='/default/import.mako',
             permission='import')
def myimport(request):
    return import_(Role, request)

###########################################################################
#                               REST SERVICE                              #
###########################################################################

@view_config(route_name=Role.get_action_routename('list', prefix="rest"),
             renderer='json',
             request_method="GET",
             permission='list'
             )
def rest_list(request):
    return json_list(Role, request)

@view_config(route_name=Role.get_action_routename('create', prefix="rest"),
             renderer='json',
             request_method="POST",
             permission='create')
def rest_create(request):
    return json_create(Role, request)

@view_config(route_name=Role.get_action_routename('read', prefix="rest"),
             renderer='json',
             request_method="GET",
             permission='read')
def rest_read(request):
    return json_read(Role, request)

@view_config(route_name=Role.get_action_routename('update', prefix="rest"),
             renderer='json',
             request_method="PUT",
             permission='update')
def rest_update(request):
    return json_update(Role, request)

@view_config(route_name=Role.get_action_routename('delete', prefix="rest"),
             renderer='json',
             request_method="DELETE",
             permission='delete')
def rest_delete(request):
    return json_delete(Role, request)
