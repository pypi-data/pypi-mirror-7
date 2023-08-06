# -*- coding: utf-8 -*-
from .client import client
from .utils.printing import pretty_int
from .utils.tabulate import tabulate

import copy
import logging
logger = logging.getLogger('solvebio')


class Filter(object):
    """
    Filter objects.

    Makes it easier to create filters cumulatively using ``&`` (and),
    ``|`` (or) and ``~`` (not) operations.

    For example::

        f = F()
        f &= F(price='Free')
        f |= F(style='Mexican')

    creates a filter "price = 'Free' or style = 'Mexican'".

    Each set of kwargs in a `Filter` are ANDed together:

        * `<field>=''` uses a term filter (exact term)
        * `<field>__in=[]` uses a terms filter (match any)

    String terms are not analyzed and are always assumed to be exact matches.

    Numeric columns can be selected by range using:

        * `<field>__gt`: greater than
        * `<field>__gte`: greater than or equal to
        * `<field>__lt`: less than
        * `<field>__lte`: less than or equal to

    Field action examples:

        dataset.query(gene__in=['BRCA', 'GATA3'],
                      chr='3',
                      start__gt=10000,
                      end__lte=20000)
    """
    def __init__(self, **filters):
        """Creates a Filter"""
        filters = filters.items()
        if len(filters) > 1:
            self.filters = [{'and': filters}]
        else:
            self.filters = filters

    def __repr__(self):
        return '<Filter {0}>'.format(self.filters)

    def _combine(self, other, conn='and'):
        """
        OR and AND will create a new Filter, with the filters from both Filter
        objects combined with the connector `conn`.
        """
        f = Filter()

        self_filters = copy.deepcopy(self.filters)
        other_filters = copy.deepcopy(other.filters)

        if not self.filters:
            f.filters = other_filters
        elif not other.filters:
            f.filters = self_filters
        elif conn in self.filters[0]:
            f.filters = self_filters
            f.filters[0][conn].extend(other_filters)
        elif conn in other.filters[0]:
            f.filters = other_filters
            f.filters[0][conn].extend(self_filters)
        else:
            f.filters = [{conn: self_filters + other_filters}]

        return f

    def __or__(self, other):
        return self._combine(other, 'or')

    def __and__(self, other):
        return self._combine(other, 'and')

    def __invert__(self):
        f = Filter()
        self_filters = copy.deepcopy(self.filters)
        if len(self_filters) == 0:
            # no change
            f.filters = []
        elif (len(self_filters) == 1
              and isinstance(self_filters[0], dict)
              and self_filters[0].get('not', {})):
            # if the filters are already a single dictionary containing a 'not'
            # then swap out the 'not'
            f.filters = self_filters[0]['not']
        else:
            # length of self_filters should never be more than 1
            # 'not' blocks can contain only dicts or a single tuple filter
            # so we get the first element from the filter list
            f.filters = [{'not': self_filters[0]}]

        return f


class RangeFilter(Filter):
    """
    Helper class that generates Range Filters
    """
    # TODO: normalize range query values

    RANGE_CHROMOSOME = '_range_chromosome'
    RANGE_START = '_range_start'
    RANGE_END = '_range_end'
    RANGE_STRAND = '_range_strand'

    def __init__(self, chromosome, start, end, strand=None, overlap=False):
        """
        Shortcut to do range queries on supported datasets.

        start and end should be positive integers.
        chromosome should be in the format 'chrN'.
        """
        chromosome, start, end = str(chromosome), str(start), str(end)

        f = Filter(**{self.RANGE_START + '__range': [start, end]})

        if overlap:
            f = f | Filter(**{self.RANGE_END + '__range': [start, end]})
        else:
            f = f & Filter(**{self.RANGE_END + '__range': [start, end]})

        f = f & Filter(**{self.RANGE_CHROMOSOME: chromosome})

        if strand is not None:
            f = f & Filter(**{self.RANGE_STRAND: strand})

        self.filters = f.filters

    def __repr__(self):
        return '<RangeFilter {0}>'.format(self.filters)


class Query(object):
    """
    A Query API request wrapper that generates a request from Filter objects,
    and can iterate through streaming result sets.
    """

    def __init__(self, data_url, **params):
        self._data_url = data_url
        self._mode = params.get('mode', 'offset')
        self._limit = params.get('limit', 100)  # results per request
        self._result_class = params.get('result_class', dict)
        self._debug = params.get('debug', False)
        self._fields = params.get('fields', None)
        self._filters = list()
        self._response = None  # the cache response

        # manages iteration of records across multiple requests
        self._slice_start = None
        self._slice_stop = None
        self._window = None  # the index range of results received
        self._i = 0  # internal result cache iterator

        # parameter error checking
        if self._limit < 0:
            raise Exception('"limit" parameter must be >= 0')

    def _clone(self, filters=None):
        new = self.__class__(self._data_url,
                             mode=self._mode,
                             limit=self._limit,
                             result_class=self._result_class)
        new._fields = self._fields
        new._filters += self._filters
        if filters is not None:
            new._filters += filters
        return new

    def filter(self, *filters, **kwargs):
        """
        Returns this Query instance with the query args combined with
        existing set with AND.

        kwargs are simply passed to a new Filter object and combined to any
        other filters with AND.

        By default, everything is combined using AND. If you provide
        multiple filters in a single filter call, those are ANDed
        together. If you provide multiple filters in multiple filter
        calls, those are ANDed together.

        If you want something different, use the F class which supports
        ``&`` (and), ``|`` (or) and ``~`` (not) operators. Then call
        filter once with the resulting Filter instance.
        """
        return self._clone(filters=list(filters) + [Filter(**kwargs)])

    def range(self, chromosome, start, end, strand=None, overlap=True):
        """
        Shortcut to do range queries on supported datasets.

        start and end should be positive integers.
        chromosome should be in the format 'chrN'.
        """
        # TODO: ensure dataset supports range queries?
        return self._clone(
            filters=[RangeFilter(chromosome, start, end, strand, overlap)])

    def _process_filters(self, filters):
        """Takes a list of filters and returns JSON

        :arg filters: list of Filters, (key, val) tuples, or dicts

        :returns: list of JSON API filters
        """
        rv = []
        for f in filters:
            if isinstance(f, Filter):
                if f.filters:
                    rv.extend(self._process_filters(f.filters))
                    continue

            elif isinstance(f, dict):
                key = f.keys()[0]
                val = f[key]

                if isinstance(val, dict):
                    filter_filters = self._process_filters(val)
                    if len(filter_filters) == 1:
                        filter_filters = filter_filters[0]
                    rv.append({key: filter_filters})
                else:
                    rv.append({key: self._process_filters(val)})
            else:
                rv.extend((f,))
        return rv

    def __len__(self):
        """Executes query and returns the total number of results"""
        if self._slice_start is not None:
            start = self._slice_start
        else:
            start = 0

        if self._slice_stop is not None and self._slice_stop <= self.total:
            stop = self._slice_stop
        else:
            stop = self.total

        return stop - start

    def __nonzero__(self):
        return bool(self.total)

    def __repr__(self):
        if self.total == 0 or self._limit == 0:
            return u'Query returned 0 results'

        return u'\n%s\n\n... %s more results.' % (
            tabulate(self[0].items(), ['Fields', 'Data'],
                     aligns=['right', 'left']),
            pretty_int(self.total - 1))

    def __getattr__(self, key):
        if self._response is None:
            logger.debug('Warming up the Query response cache')
            self.execute()

        if key in self._response.keys():
            return self._response[key]

        raise AttributeError(key)

    def __getitem__(self, key):
        """
        Retrieve an item or slice from the set of results
        """
        if not isinstance(key, (slice, int, long)):
            raise TypeError

        # prevent indexing when limit is 0
        assert (self._limit > 0), "Indexing not supported when limit == 0."

        # prevent negative indexing
        assert (
            (not isinstance(key, slice) and (key >= 0)) or
            (isinstance(key, slice) and (key.start is None or key.start >= 0)
                and (key.stop is None or key.stop >= 0))
            ), "Negative indexing is not supported."

        # if the cache is warmed up, see if we have the results
        if self._response is not None:
            lower, upper = self._window

            if isinstance(key, slice):
                # double slices and single stop slices are handled
                if key.stop is not None and int(key.stop) <= upper:
                    if key.start is None or (key.start is not None
                                             and int(key.start) >= lower):
                        return self.results[key]
            elif lower <= key < upper:
                return self.results[key]

        # the result is not yet cached so we need to start fresh
        new = self._clone()

        if isinstance(key, slice):
            if key.start is not None:
                new._slice_start = int(key.start)
            if key.stop is not None:
                new._slice_stop = int(key.stop)

            if key.step:
                return list(new)[::key.step]
            else:
                return list(new)

        # not a slice, just an single index
        new._slice_start = key
        new._slice_stop = key + 1

        return list(new)[0]

    def __iter__(self):
        """
        Execute a query and iterate through the result set.
        Once the cached result set is exhausted, repeat query.
        """
        # always start fresh
        self.execute()

        # start the internal counter _i
        self._i = self._slice_start or 0

        # fast-forward the cursor if needed
        while self._window[1] < self._i:
            self.execute(**{self._mode: self._response[self._mode]})

        # slice the results_cache to put _start at 0 in the cache
        self._response['results'] = \
            self._response['results'][self._i - self._window[0]:]

        return self

    def next(self):
        """
        Allows the Query object to be an iterable.
        Iterates through the internal cache using a cursor.
        """
        # See if the cursor has reached the end
        if (self._slice_stop is not None and self._i >= self._slice_stop) \
                or self._i >= self.total:
            raise StopIteration

        # If there is no window (limit == 0), also stop
        if self._i == self._window[1] == 0:
            raise StopIteration

        # get the index within the current window
        cache_index = self._i - self._window[1]
        if cache_index == 0:
            # current result cache is empty, request more
            self.execute(**{self._mode: self._response[self._mode]})
            cache_index = self._i - self._window[1]

        self._i += 1
        return self.results[cache_index]

    def _recalculate_window(self, response, params):
        """
        Recalculate the window of retrieved results so we can handle slicing.
        """
        results_in_response = len(response['results'])

        if self._mode == 'cursor':
            # cursor mode
            if self._window is None:
                # if cursor mode and no response yet, assume we're at 0
                return [0, results_in_response]
            else:
                # if cursor and previous window, increment the previous window
                return[self._window[1], self._window[1] + results_in_response]
        else:
            # offset mode
            if response.get('offset', None) is not None:
                # if offset mode, just use the offset if it exists
                return [response['offset'] - results_in_response,
                        response['offset']]
            elif params.get('offset', None) is not None:
                # no offset found in the response... use the request params
                return [params['offset'],
                        params['offset'] + results_in_response]

        return [0, results_in_response]

    def _build_query(self):
        q = {
            'mode': self._mode,
            'limit': self._limit,
            'debug': self._debug
        }

        if self._filters:
            filters = self._process_filters(self._filters)
            if len(filters) > 1:
                q['filters'] = [{'and': filters}]
            else:
                q['filters'] = filters

        if self._fields is not None:
            q['fields'] = self._fields

        return q

    def execute(self, **params):
        """
        Executes a query and returns the request parameters and response.
        """
        params.update(self._build_query())
        logger.debug('Querying dataset: %s' % str(params))
        response = client.request('post', self._data_url, params)
        logger.debug('Query response Took %(took)d Total %(total)d' % response)

        if response['mode'] != self._mode:
            logger.info('Server modified the query mode from %s to %s',
                        self._mode, response['mode'])
            self._mode = response['mode']

        self._window = self._recalculate_window(response, params)
        logger.debug('Query response window [%d, %d]'
                     % (self._window[0], self._window[1]))

        response['results'] = [self._result_class(r)
                               for r in response['results']]

        if self._slice_start is not None \
                and self._slice_start >= response['total']:
            raise IndexError(
                'Index out of range, only %d total results(s)'
                % self.total)

        self._response = response
        return params, response
