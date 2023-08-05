from django.conf.urls import url

from .models import (
    ENTITY_LAYER, ENTITY_LIST, ENTITY_JSON_LIST,
    ENTITY_FORMAT_LIST, ENTITY_DETAIL, ENTITY_MAPIMAGE, ENTITY_DOCUMENT, ENTITY_CREATE,
    ENTITY_UPDATE, ENTITY_DELETE,
)


frommodel = lambda model: model.__name__.lower()


def url_layer(model):
    model_str = frommodel(model)
    return r'^api/{0}/{1}.geojson$'.format(model_str, model_str)


def url_list(model):
    return r'^{0}/list/$'.format(frommodel(model))


def url_json_list(model):
    model_str = frommodel(model)
    return r'^api/{0}/{1}s.json$'.format(model_str, model_str)


def url_format_list(model):
    return r'^{0}/list/export/$'.format(frommodel(model))


def url_detail(model):
    return r'^{0}/(?P<pk>\d+)/$'.format(frommodel(model))


def url_mapimage(model):
    return r'^image/{0}-(?P<pk>\d+).png$'.format(frommodel(model))


def url_document(model):
    return r'^document/{0}-(?P<pk>\d+).odt$'.format(frommodel(model))


def url_create(model):
    return r'^{0}/add/$'.format(frommodel(model))


def url_update(model):
    return r'^{0}/edit/(?P<pk>\d+)/$'.format(frommodel(model))


def url_delete(model):
    return r'^{0}/delete/(?P<pk>\d+)/$'.format(frommodel(model))


kind_to_urlpath = {
    ENTITY_LAYER: url_layer,
    ENTITY_LIST: url_list,
    ENTITY_JSON_LIST: url_json_list,
    ENTITY_FORMAT_LIST: url_format_list,
    ENTITY_DETAIL: url_detail,
    ENTITY_MAPIMAGE: url_mapimage,
    ENTITY_DOCUMENT: url_document,
    ENTITY_CREATE: url_create,
    ENTITY_UPDATE: url_update,
    ENTITY_DELETE: url_delete,
}


def view_class_to_url(view_class):
    kind = view_class.get_entity_kind()

    # TODO: Should raise an error
    if not kind:
        return None

    model = view_class.model or view_class.queryset.model
    url_name = model.get_url_name_for_registration(kind)
    url_path = kind_to_urlpath[kind](model)
    return url(url_path, view_class.as_view(), name=url_name)


def view_classes_to_url(*view_classes):
    return [view_class_to_url(view_class) for view_class in view_classes]
