from pyramid import httpexceptions
from sqlalchemy.orm import Query

from pyramid_views import utils
from pyramid_views.paginator import Paginator, InvalidPage
from pyramid_views.utils import ImproperlyConfigured, _
from pyramid_views.views.base import ContextMixin, View, TemplateResponseMixin, DbSessionMixin, MacroMixin


class MultipleObjectMixin(DbSessionMixin, MacroMixin, ContextMixin):
    """
    A mixin for views manipulating multiple objects.
    """
    allow_empty = True
    query = None
    model = None
    paginate_by = None
    paginate_orphans = 0
    context_object_name = None
    paginator_class = Paginator
    page_kwarg = 'page'

    def get_query(self):
        """
        Return the list of items for this view.

        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        if self.query is not None:
            query = self.query
        elif self.model is not None:
            query = self.db_session.query(self.model)
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a Query. Define "
                "%(cls)s.model, %(cls)s.query, or override "
                "%(cls)s.get_query()." % {
                    'cls': self.__class__.__name__
                }
            )

        # Set the session on the query if it doesn't have one
        if isinstance(query, Query) and not query.session:
            query.session = self.db_session

        return query

    def paginate_query(self, query, page_size):
        """
        Paginate the query, if needed.
        """
        paginator = self.get_paginator(
            query, page_size, orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty())
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise httpexceptions.HTTPNotFound(_("Page is not 'last', nor can it be converted to an int."))
        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage as e:
            raise httpexceptions.HTTPNotFound(_('Invalid page (%(page_number)s): %(message)s') % {
                'page_number': page_number,
                'message': str(e)
            })

    def get_paginate_by(self, query):
        """
        Get the number of items to paginate by, or ``None`` for no pagination.
        """
        return self.paginate_by

    def get_paginator(self, query, per_page, orphans=0,
                      allow_empty_first_page=True, **kwargs):
        """
        Return an instance of the paginator for this view.
        """
        return self.paginator_class(
            query, per_page, orphans=orphans,
            allow_empty_first_page=allow_empty_first_page, **kwargs)

    def get_paginate_orphans(self):
        """
        Returns the maximum number of orphans extend the last page by when
        paginating.
        """
        return self.paginate_orphans

    def get_allow_empty(self):
        """
        Returns ``True`` if the view should display empty lists, and ``False``
        if a 404 should be raised instead.
        """
        return self.allow_empty

    def get_context_object_name(self, object_list):
        """
        Get the name of the item to be used in the context.
        """
        if self.context_object_name:
            return self.context_object_name
        elif isinstance(object_list, Query):
            return '%s_list' % utils.model_from_query(object_list).__tablename__
        else:
            return None

    def get_context_data(self, **kwargs):
        """
        Get the context for this view.
        """
        query = kwargs.pop('object_list', self.object_list)
        page_size = self.get_paginate_by(query)
        context_object_name = self.get_context_object_name(query)
        if page_size:
            paginator, page, query, is_paginated = self.paginate_query(query, page_size)
            context = {
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
                'object_list': query
            }
        else:
            context = {
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                'object_list': query
            }
        if context_object_name is not None:
            context[context_object_name] = query
        context.update(kwargs)
        return super(MultipleObjectMixin, self).get_context_data(**context)


class BaseListView(MultipleObjectMixin, View):
    """
    A base view for displaying a list of objects.
    """
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_query()
        allow_empty = self.get_allow_empty()
        if not allow_empty:
            # When pagination is enabled and object_list is a query,
            # it's better to do a cheap query than to load the unpaginated
            # query in memory.
            if (self.get_paginate_by(self.object_list) is not None
                    and hasattr(self.object_list, 'exists')):
                is_empty = not self.object_list.session.query(self.object_list.exists()).scalar()
            else:
                is_empty = self.object_list.count() == 0
            if is_empty:
                raise httpexceptions.HTTPNotFound(_("Empty list and '%(class_name)s.allow_empty' is False.")
                        % {'class_name': self.__class__.__name__})
        context = self.get_context_data()
        return self.render_to_response(context)


class MultipleObjectTemplateResponseMixin(TemplateResponseMixin):
    """
    Mixin for responding with a template and list of objects.
    """
    template_name_suffix = '_list'
    template_extension = '.pt'

    def get_template_names(self):
        """
        Return a list of template names to be used for the request. Must return
        a list. May not be called if render_to_response is overridden.
        """
        try:
            names = super(MultipleObjectTemplateResponseMixin, self).get_template_names()
        except ImproperlyConfigured:
            # If template_name isn't specified, it's not a problem --
            # we just start with an empty list.
            names = []

        # If the list is a query, we'll invent a template name based on the
        # app and model name. This name gets put at the end of the template
        # name list so that user-supplied names override the automatically-
        # generated ones.
        if isinstance(self.object_list, Query):
            model = utils.model_from_query(self.object_list)
            package = utils.get_template_package_name(model)
            names.append("%s:templates/%s%s%s" % (package, model.__tablename__,
                                                   self.template_name_suffix, self.template_extension))

        # For benefit of tests
        self._template_names = names

        return names


class ListView(MultipleObjectTemplateResponseMixin, BaseListView):
    """
    Render some list of objects, set by ``self.model`` or ``self.query``.
    ``self.query`` can actually be any iterable of items, not just a query.
    """
