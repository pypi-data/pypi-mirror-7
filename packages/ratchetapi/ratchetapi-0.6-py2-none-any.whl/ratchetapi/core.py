# coding: utf-8
import re
import logging
import time
import functools

from . import httpbroker
from . import exceptions


logger = logging.getLogger(__name__)

ITEMS_PER_REQUEST = 20
API_VERSIONS = ('v1',)
RESOURCE_PATH_PATTERN = re.compile(r'/api/(\w+)/(\w+)/(\d+)/')


class Connector(object):
    """
    Encapsulates the HTTP requests layer.

    :param username: (optional) valid username that has access to ratchet.scielo.org. Mandatory for POST actions.
    :param api_key: (optional) its respective api key. Mandatory for POST actions.
    :param api_uri: (optional) if connecting to a non official instance of `Ratchet SciELO Manager <https://github.com/scieloorg/ratchet>`_
    :param version: (optional) by default the newest version is used.
    :param http_broker: (optional) a module to deal with http stuff. The reference API is implemented at :mod:`scieloapi.httpbroker`.
    :param check_ca: (optional) if certification authority should be checked during ssl sessions. Defaults to `False`.
    """
    # caches endpoints definitions
    _cache = {}

    def __init__(self, username=None, api_key=None, api_uri=None,
                 version=None, http_broker=None, check_ca=False):
        # dependencies
        self._time = time

        if http_broker:
            _httpbroker = http_broker
        else:
            _httpbroker = httpbroker  # module

        # setup
        self.check_ca = check_ca
        self.api_uri = api_uri if api_uri else r'http://ratchet.scielo.org/api/'

        if version:
            if version in API_VERSIONS:
                self.version = version
            else:
                raise ValueError('unsupported api version. supported are: %s' % ', '.join(API_VERSIONS))
        else:
            self.version = sorted(API_VERSIONS)[-1]

        self.username = username
        self.api_uri = self.api_uri + self.version + '/'

        # dynamic http methods creation
        self._create_http_methods(_httpbroker, username, api_key)

    def _create_http_methods(self, broker, username, api_key):
        """
        Dynamically adds http methods bound to user credentials.

        :param broker: reference to the module to be used as http broker.
        :param username: valid username that has access to ratchet.scielo.org. Mandatory for POST actions.
        :param api_key: its respective api key. Mandatory for POST actions.
        """
        bound_get = functools.partial(broker.get, auth=(username, api_key),
            check_ca=self.check_ca)

        setattr(self, '_http_get', bound_get)

    def fetch_data(self, endpoint,
                         resource_id=None,
                         **kwargs):
        """
        Fetches the specified resource from the SciELO Manager API.

        :param endpoint: a valid endpoint at http://ratchet.scielo.org/api/v1/
        :param resource_id: (optional) an int representing the document.
        :param \*\*kwargs: (optional) params to be passed as query string.
        """
        err_count = 0

        while True:
            try:
                response = self._http_get(self.api_uri,
                                          endpoint=endpoint,
                                          resource_id=resource_id,
                                          params=kwargs)

            except (exceptions.ConnectionError, exceptions.ServiceUnavailable) as e:
                if err_count < 10:
                    wait_secs = err_count * 5
                    logger.info('%s. Waiting %ss to retry.' % (e, wait_secs))
                    self._time.sleep(wait_secs)
                    err_count += 1
                    continue
                else:
                    logger.error('%s. Unable to connect to resource.' % e)
                    raise
            else:
                # restart error count
                err_count = 0
                return response

    def iter_docs(self, endpoint, **kwargs):
        """
        Iterates over all documents of a given endpoint and collection.

        :param endpoint: must be a valid endpoint at http://ratchet.scielo.org/api/v1/
        :param \*\*kwargs: are passed thru the request as query string params
        """
        offset = 0
        limit = ITEMS_PER_REQUEST

        qry_params = {'limit': limit}
        qry_params.update(kwargs)

        while True:
            qry_params.update({'offset': offset})
            doc = self.fetch_data(endpoint, **qry_params)

            for obj in doc['objects']:
                # we are interested only in non-trashed items.
                if obj.get('is_trashed'):
                    continue

                yield obj

            if not doc['meta']['next']:
                raise StopIteration()
            else:
                offset += ITEMS_PER_REQUEST

    def get_endpoints(self):
        """
        Get all endpoints available for the given API version.
        """
        cls = self.__class__

        if self.version not in cls._cache:
            cls._cache[self.version] = self._http_get(self.api_uri)

        return cls._cache[self.version]


class Endpoint(object):
    """
    Represents an API endpoint.

    :param name: the endpoint name.
    :param connector: instance of :class:`Connector`.
    """
    def __init__(self, name, connector):
        self.name = name
        self.connector = connector

    def get(self, resource_id):
        """
        Gets a specific document of the endpoint.

        :param resource_id: an int representing the document.
        """
        res = self.connector.fetch_data(self.name, resource_id=resource_id)
        return res

    def all(self):
        """
        Gets all documents of the endpoint.
        """
        return self.connector.iter_docs(self.name)

    def filter(self, **kwargs):
        """
        Gets all documents of the endpoint that satisfies some criteria.

        :param \*\*kwargs: filtering criteria as documented at `docs.scielo.org <http://ref.scielo.org/ph6gvk>`_
        """
        return self.connector.iter_docs(self.name, **kwargs)


class Client(object):
    """
    Collection of :class:`Endpoint` made available in an object oriented fashion.

    An instance of Client tries to figure out the available endpoints
    for the version of the API the Client is instantiated for, and
    automatically instantiates :class:`Endpoint` for each one.
    If ``version`` is missing, the newest available will be used.

    :param username: (optional) valid username that has access to ratchet.scielo.org. Mandatory for POST actions.
    :param api_key: (optional) its respective api key. Mandatory for POST actions.
    :param api_uri: (optional) if connecting to a non official instance of `Ratchet SciELO <https://github.com/scieloorg/ratchet>`_
    :param version: (optional) by default the newest version is used.
    :param check_ca: (optional) if certification authority should be checked during ssl sessions. Defaults to `False`.

    Usage::

        >>> import scieloapi
        >>> cli = scieloapi.Client('some.user', 'some.apikey')
        <scieloapi.scieloapi.Client object at 0x10726f9d0>
        >>> cli.query('journals').all()
        <generator object iter_docs at 0x10fd59730>
    """
    def __init__(self, username=None, api_key=None, api_uri=None,
                 version=None, connector_dep=Connector, check_ca=False):

        self._connector = connector_dep(username,
                                        api_key,
                                        api_uri=api_uri,
                                        version=version,
                                        check_ca=check_ca)
        self._endpoints = {}
        for ep in self._introspect_endpoints():
            self._endpoints[ep] = Endpoint(ep, self._connector)

    def _introspect_endpoints(self):
        """
        Contact the API server to discover the available endpoints.
        """
        return self._connector.get_endpoints().keys()

    def __getattr__(self, name):
        """
        Missing attributes are assumed to be endpoint lookups.
        i.e. Client.journals.all()
        """
        if name in self._endpoints:
            logger.warning('DEPRECATION WARNING! Use the `query` method for endpoint lookups.')
            return self._endpoints[name]
        else:
            raise AttributeError()

    @property
    def endpoints(self):
        """
        Lists all available endpoints for the api version
        the instance of :class:`Client` was created to interact.
        """
        return self._endpoints.keys()

    @property
    def version(self):
        """
        The API version the Client instance is interfacing with.
        """
        return self._connector.version

    def fetch_relations(self, dataset, only=None):
        """
        Fetches all records that relates to `dataset`.

        Its important to note that only first-level relations will be fetched
        in order to avoid massive data retrieval.

        :param dataset: datastructure representing a record. Tipically a `dict` instance.
        :param only: (optional) a collection of relations to fetch. By default, all relations are retrieved.

        Usage::

            >>> import scieloapi
            >>> cli = scieloapi.Client('some.user', 'some.apikey')
            >>> cli.fetch_relations(cli.journals.get(70))
        """
        new_dataset = {}

        for attr_name, attr_value in dataset.items():
            # skip fetching itself and undesired fields
            if attr_name == 'resource_uri' or (only and attr_name not in only):
                new_dataset[attr_name] = attr_value
            elif isinstance(attr_value, basestring):
                try:
                    new_dataset[attr_name] = self.get(attr_value)
                except ValueError as e:
                    new_dataset[attr_name] = attr_value

            elif isinstance(attr_value, list):
                new_elems = []
                for elem in attr_value:
                    try:
                        new_elems.append(self.get(elem))
                    except (TypeError, ValueError) as e:
                        new_elems.append(elem)

                new_dataset[attr_name] = new_elems
            else:
                new_dataset[attr_name] = attr_value

        return new_dataset

    def get(self, resource_uri):
        """
        Gets resource_uri.

        Gets the given resource in a opinionated fashion in terms of the
        `version` passed during client's instantiation. The `endpoint` must also
        be available for the version the client is bound to.

        :param resource_uri: text string in the form `/api/<version>/<endpoint>/<resource_id>/`.
        """
        match = RESOURCE_PATH_PATTERN.match(resource_uri)
        if match:
            version, endpoint, resource_id = match.groups()

            if version != self.version:
                raise ValueError('Resource and Client version must match')

            return self.query(endpoint).get(resource_id)
        else:
            raise ValueError('Invalid resource_uri')

    def query(self, endpoint):
        """
        Query an endpoint.

        :param endpoint: string of the endpoint's name. A complete list of
        valid endpoints can be got at :attr:`Client.endpoints`.
        """
        if endpoint in self._endpoints:
            return self._endpoints[endpoint]
        else:
            raise ValueError('Unknown endpoint %s.' % endpoint)
