from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask import g, request, url_for
from flask.ext.login import current_user


def app_template_filter(filter_name=''):
    def wrap(f):
        if not hasattr(f, '_filter'):
            f._filter = filter_name
        return f
    return wrap


class TemplateFilters(object):
    
    security_manager = None
    
    def __init__(self, app, security_manager):
        self.security_manager = security_manager
        for attr_name in dir(self):
            if hasattr(getattr(self, attr_name),'_filter'):
                attr = getattr(self, attr_name)
                app.jinja_env.filters[attr._filter] = attr


    @app_template_filter('link_order')
    def link_order_filter(self, column, generalview_name):
        """
            Arguments are passed like: _oc_<VIEW_NAME>=<COL_NAME>&_od_<VIEW_NAME>='asc'|'desc'
        """
        new_args = request.view_args.copy()
        args = request.args.copy()
        if ('_oc_' + generalview_name) in args:
            args['_oc_' + generalview_name] = column
            if args.get('_od_' + generalview_name) == 'asc':
                args['_od_' + generalview_name] = 'desc'
            else:
                args['_od_' + generalview_name] = 'asc'
        else:
            args['_oc_' + generalview_name] = column
            args['_od_' + generalview_name] = 'asc'
        return url_for(request.endpoint,**dict(list(new_args.items()) + list(args.to_dict().items())))

    @app_template_filter('link_page')
    def link_page_filter(self, page, generalview_name):
        """
            Arguments are passed like: page_<VIEW_NAME>=<PAGE_NUMBER>
        """
        new_args = request.view_args.copy()
        args = request.args.copy()
        args['page_' + generalview_name] = page
        return url_for(request.endpoint, **dict(list(new_args.items()) + list(args.to_dict().items())))


    @app_template_filter('link_page_size')
    def link_page_size_filter(self, page_size, generalview_name):
        """
        Arguments are passed like: psize_<VIEW_NAME>=<PAGE_NUMBER>
        """
        new_args = request.view_args.copy()
        args = request.args.copy()
        args['psize_' + generalview_name] = page_size
        return url_for(request.endpoint, **dict(list(new_args.items()) + list(args.to_dict().items())))


    @app_template_filter('get_link_next')
    def get_link_next_filter(self, s):
        return request.args.get('next')
        
    @app_template_filter('get_link_back')
    def get_link_back_filter(self, request):
        return request.args.get('next') or request.referrer
    

    # TODO improve this
    @app_template_filter('set_link_filters')
    def set_link_filters_filter(self, path, filters):
        lnkstr = path
        for flt, value in filters.get_filters_values():
            if flt.is_related_view:
                lnkstr = lnkstr + '&_flt_0_' + flt.column_name + '=' + str(value)
        return lnkstr

    @app_template_filter('get_link_order')
    def get_link_order_filter(self, column, generalview_name):
        if request.args.get('_oc_' + generalview_name) == column:
            if (request.args.get('_od_' + generalview_name) == 'asc'):
                return 2
            else:
                return 1
        else:
            return 0

    @app_template_filter('get_attr')
    def get_attr_filter(self, obj, item):
        return getattr(obj, item)


    @app_template_filter('is_menu_visible')
    def is_menu_visible(self, item):
        return self.security_manager.has_access("menu_access", item.name)

    @app_template_filter('is_item_visible')
    def is_item_visible(self, permission, item):
        return self.security_manager.has_access(permission, item)

