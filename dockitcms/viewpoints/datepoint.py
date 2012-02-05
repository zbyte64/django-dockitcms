from listpoint import ListViewPoint

from django import forms
from django.conf.urls.defaults import patterns, url
from django.utils.translation import ugettext_lazy as _
from django.views.generic.dates import DayMixin, MonthMixin, YearMixin, DateMixin

from dockitcms.utils import ConfigurableTemplateResponseMixin

import dockit
from dockit.views import ListView, DetailView


class PointDetailView(ConfigurableTemplateResponseMixin, DetailView):
    pass

class BaseDateListView(ConfigurableTemplateResponseMixin, DateMixin, ListView):
    """
    Abstract base class for date-based views display a list of objects.
    """
    allow_empty = False

    def get(self, request, *args, **kwargs):
        self.date_list, self.object_list, extra_context = self.get_dated_items()
        context = self.get_context_data(object_list=self.object_list,
                                        date_list=self.date_list)
        context.update(extra_context)
        return self.render_to_response(context)
    
    def get_lookup_kwargs(self):
        raise NotImplementedError
    
    def get_dated_items(self):
        """
        Return (date_list, items, extra_context) for this request.
        """
        # Yes, no error checking: the URLpattern ought to validate this; it's
        # an error if it doesn't.
        lookup = self.get_lookup_kwargs()
        object_list = self.get_dated_queryset(**lookup)
        date_list = self.get_date_list(**lookup)

        return (date_list, object_list, lookup)

    def get_dated_queryset(self, **lookup):
        """
        Get a queryset properly filtered according to `allow_future` and any
        extra lookup kwargs.
        """
        #qs = self.document.objects
        date_field = self.get_date_field()
        allow_future = self.get_allow_future()
        allow_empty = self.get_allow_empty()

        #if not allow_future:
        #    qs = qs.filter(**{'%s__lte' % date_field: datetime.datetime.now()})
        
        qs = getattr(self.document.objects.filter, date_field)(**lookup)

        #if not allow_empty and not qs:
        #    raise Http404(_(u"No %(verbose_name_plural)s available") % {
        #            'verbose_name_plural': force_unicode(qs.model._meta.verbose_name_plural)
        #    })

        return qs

    def get_date_list(self, **lookup):
        """
        Get a date list by calling `queryset.dates()`, checking along the way
        for empty lists that aren't allowed.
        """
        date_field = self.get_date_field()
        allow_empty = self.get_allow_empty()

        #date_list = queryset.dates(date_field, date_type)[::-1]
        #if date_list is not None and not date_list and not allow_empty:
        #    raise Http404(_(u"No %(verbose_name_plural)s available") % {
        #            'verbose_name_plural': force_unicode(qs.model._meta.verbose_name_plural)
        #    })
        #TODO signal we want month as opposed to days, etc
        date_list = getattr(self.document.objects.values, date_field)(**lookup)

        return date_list

    def get_context_data(self, **kwargs):
        """
        Get the context. Must return a Context (or subclass) instance.
        """
        items = kwargs.pop('object_list')
        context = super(BaseDateListView, self).get_context_data(object_list=items)
        context.update(kwargs)
        return context

class DatePointListView(BaseDateListView):
    def get_lookup_kwargs(self):
        return {}

class YearDatePointListView(YearMixin, BaseDateListView):
    def get_lookup_kwargs(self):
        return {'year':self.get_year()}

class MonthDatePointListView(YearDatePointListView, MonthMixin):
    def get_lookup_kwargs(self):
        kwargs = super(MonthDatePointListView, self).get_lookup_kwargs()
        kwargs['month'] = self.get_month()
        return kwargs

class DayDatePointListView(MonthDatePointListView, DayMixin):
    def get_lookup_kwargs(self):
        kwargs = super(DayDatePointListView, self).get_lookup_kwargs()
        kwargs['day'] = self.get_day()
        return kwargs

class DateListViewPoint(ListViewPoint):
    date_field = dockit.CharField(help_text=_('Dotpoint notation to the date field')) #TODO turn into a choice field
    day_format = dockit.CharField(default='%d')
    month_format = dockit.CharField(default='%b')
    year_format = dockit.CharField(default='%Y')
    allow_future = dockit.BooleanField(default=False)
    
    list_view_class = DatePointListView
    detail_view_class = PointDetailView
    
    class Meta:
        typed_key = 'datelist'

    def register_view_point(self):
        doc_cls = self.collection.get_document()
        field = self.date_field
        doc_cls.objects.enable_index("date", field, {'field':field})
        print 'enabled for', field
        ListViewPoint.register_view_point(self)
    
    def get_urls(self):
        document = self.get_document()
        params = self.to_primitive(self)
        list_configuration = self._configuration_from_prefix(params, 'list')
        urlpatterns = patterns('',
            url(r'^$', 
                self.list_view_class.as_view(document=document,
                                      allow_future=params.get('allow_future', False),
                                      date_field=params['date_field'],
                                      configuration=list_configuration,
                                      paginate_by=params.get('paginate_by', None)),
                name='index',
            ),
            url(r'^(?P<year>[\d]+)/$', 
                YearDatePointListView.as_view(document=document,
                                              allow_future=params.get('allow_future', False),
                                              date_field=params['date_field'],
                                              year_format=params['year_format'],
                                              configuration=list_configuration,),
                name='year',
            ),
            url(r'^(?P<year>[\d]+)/(?P<month>[\d]+)/$', 
                MonthDatePointListView.as_view(document=document,
                                              allow_future=params.get('allow_future', False),
                                              date_field=params['date_field'],
                                              year_format=params['year_format'],
                                              month_format=params['month_format'],
                                              configuration=list_configuration,),
                name='month',
            ),
            url(r'^(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<day>[\d]+)/$',
                DayDatePointListView.as_view(document=document,
                                              allow_future=params.get('allow_future', False),
                                              date_field=params['date_field'],
                                              year_format=params['year_format'],
                                              month_format=params['month_format'],
                                              day_format=params['day_format'],
                                              configuration=list_configuration,),
                name='day',
            ),
        )
        if params.get('slug_field', None):
            urlpatterns += patterns('',
                url(r'^(?P<slug>.+)/$', 
                    self.detail_view_class.as_view(document=document,
                                            slug_field=params['slug_field'],
                                            configuration=self._configuration_from_prefix(params, 'detail'),),
                    name='detail',
                ),
            )
        else:
            urlpatterns += patterns('',
                url(r'^(?P<pk>.+)/$', 
                    self.detail_view_class.as_view(document=document,
                                            configuration=self._configuration_from_prefix(params, 'detail'),),
                    name='detail',
                ),
            )
        return urlpatterns

