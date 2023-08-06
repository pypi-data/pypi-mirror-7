# -*- coding: utf-8 -*-

import slumber


class Client(object):

    class_instance = None


    def __init__(self, hostname, protocol='http', port=8529, database='_system'):
        """
        """

        Client.class_instance = self

        url = '%s://%s:%s/_db/%s/_api/' % (protocol, hostname, port, database)
        self.api = slumber.API(url, append_slash=False)


    @classmethod
    def instance(cls, hostname=None, protocol=None, port=None):

        if cls.class_instance is None:
            cls.class_instance = Client(hostname=hostname, protocol=protocol, port=port)
        else:
            if hostname is not None:
                cls.class_instance.hostname = hostname

            if protocol is not None:
                cls.class_instance.hostname = protocol

            if port is not None:
                cls.class_instance.hostname = port

        return cls.class_instance

    def collection(self, name):
        """
        """

        return Collection(
            name=name,
            api_resource=self.api.collection(name),
            api=self.api,
        )


class SimpleQuery(object):

    @classmethod
    def getByExample(cls, collection, example_data):
        """
        """

        query = {
            'collection': collection,
            'example': example_data,
        }

        api = Client.instance().api
        return api.simple('by-example').put(data=query)


class Query(object):

    SORTING_ASC = 'ASC'
    SORTING_DESC = 'DESC'

    def __init__(self):
        """
        """

        self.collections = []
        self.filters = []

        self.start = -1
        self.count = -1

        self.sorting = []

    def append_collection(self, collection_name):
        """
        """

        self.collections.append(collection_name)

        return self

    def filter(self, **kwargs):

        for key, value in kwargs.iteritems():

            splitted_filter = key.split('__')

            if len(splitted_filter) is 1:

                self.filters.append(
                    QueryFilterStatement(
                        collection=self.collections[-1],
                        attribute=key,
                        operator=QueryFilterStatement.EQUAL_OPERATOR,
                        value=value,
                    )
                )

            else:

                self.filters.append(
                    QueryFilterStatement(
                        collection=splitted_filter[0],
                        attribute=splitted_filter[1],
                        operator=QueryFilterStatement.EQUAL_OPERATOR,
                        value=value,
                    )
                )

        return self

    def limit(self, count, start=-1):
        self.start = start
        self.count = count

    def order_by(self, field, order=None, collection=None):

        if order is None:
            order = self.SORTING_ASC

        self.sorting.append({
            'field': field,
            'order': order,
            'collection': collection,
        })

    def execute(self):
        """
        """

        query_data = ''

        for collection in self.collections:
            query_data += ' FOR %s in %s' % (
                self._get_collection_ident(collection),
                collection
            )

        for filter_statement in self.filters:
            query_data += ' FILTER %s.%s %s %s' % (
                filter_statement.collection,
                filter_statement.attribute,
                filter_statement.operator,
                filter_statement.value,
            )

        is_first = True

        for sorting_entry in self.sorting:

            if is_first:
                query_data += ' SORT '

            if sorting_entry['field'] is not None:

                if not is_first:
                    query_data += ', '

                if sorting_entry['collection'] is not None:
                    query_data += '%s.%s %s' % (
                        self._get_collection_ident(sorting_entry['collection']),
                        sorting_entry['field'],
                        sorting_entry['order'],
                    )
                else:
                    query_data += '%s.%s %s' % (
                        self._get_collection_ident(self.collections[0]),
                        sorting_entry['field'],
                        sorting_entry['order'],
                    )

                if is_first:
                    is_first = False

        if self.count is not -1:

            if self.start is not -1:
                query_data += ' LIMIT %s, %s' % (self.start, self.count)
            else:
                query_data += ' LIMIT %s' % self.count

        query_data += ' RETURN %s' % collection + '_123'

        post_data = {
            'query': query_data
        }

        api = Client.instance().api

        result = []

        try:
            post_result = api.cursor.post(data=post_data)

            result_dict_list = post_result['result']

            # Create documents
            for result_dict in result_dict_list:

                collection_name = result_dict['_id'].split('/')[0]

                doc = Document(
                    id=result_dict['_id'],
                    key=result_dict['_key'],
                    collection=collection_name,
                    api=api,
                )

                del result_dict['_id']
                del result_dict['_key']
                del result_dict['_rev']

                for result_key in result_dict:
                    result_value = result_dict[result_key]

                    doc.setData(key=result_key, value=result_value)

                result.append(doc)


        except Exception as err:
            print(err.message)

        return  result

    def _get_collection_ident(self, collection_name):
        return collection_name + '_123'


class Traveser(object):

    @classmethod
    def follow(cls, start_vertex, edge_collection, direction):

        related_docs = []

        request_data = {
            'startVertex': start_vertex,
            'edgeCollection': edge_collection,
            'direction': direction,
        }

        api = Client.instance().api
        result_dict = api.traversal.post(data=request_data)
        results = result_dict['result']['visited']

        vertices = results['vertices']
        vertices.remove(vertices[0])

        for vertice in vertices:

            collection_name = vertice['_id'].split('/')[0]

            doc = Document(
                id=vertice['_id'],
                key=vertice['_key'],
                collection=collection_name,
                api=api,
            )

            del vertice['_id']
            del vertice['_key']
            del vertice['_rev']

            doc.data = vertice

            related_docs.append(doc)

        return related_docs


class Database(object):

    @classmethod
    def create(cls, name):
        """
        """

        api = Client.instance().api

        database_data = {
            'name': name,
            'active': True,
        }

        data = api.database.post(data=database_data)

        db = Database(
            name=name,
            api=api,
            kwargs=data
        )

        return db

    def __init__(self, name, api, **kwargs):
        """
        """

        self.name = name
        self.api = api

    def create_collection(self, name):
        """
        """

        return Collection.create(name=name, database=self)


class Collection(object):

    @classmethod
    def create(cls, name, type=2):
        """
        """

        api = Client.instance().api

        collection_data = {
            'name': name,
            'type': type,
        }

        data = api.collection.post(data=collection_data)

        collection = Collection(
            name=name,
            api_resource=api.collection,
            api=api,
            kwargs=data
        )

        return collection

    def __init__(self, name, api, **kwargs):
        """
        """
        self.name = name

        self.setData(**kwargs)

        self.resource = api.collection
        self.api = api

    def setData(self, **kwargs):
        """
        """

        if 'status' in kwargs:
            self.status = kwargs['status']
        else:
            self.status = 0

        if 'waitForSync' in kwargs:
            self.waitForSync = kwargs['waitForSync']
        else:
            self.waitForSync = False

        if 'isVolatile' in kwargs:
            self.isVolatile = kwargs['isVolatile']
        else:
            self.isVolatile = False

        if 'isSystem' in kwargs:
            self.isSystem = kwargs['isSystem']
        else:
            self.isSystem = False

        if 'type' in kwargs:
            self.type = kwargs['type']
        else:
            self.type = 2

        if 'id' in kwargs:
            self.id = kwargs['id']
        else:
            self.id = '0'

    def get(self):
        """
        """

        data = self.resource.get()

        self.setData(**data)

        return data

    def create_document(self):
        """
        """

        return Document.create(collection=self)

    def create_edge(self, from_doc, to_doc, edge_data={}):
        """
        """

        return Edge.create(
            collection=self,
            from_doc=from_doc,
            to_doc=to_doc,
            edge_data=edge_data
        )

    def get_document_by_example(self, example_data):
        """
        """

        all_docs = []

        result_dict = SimpleQuery.getByExample(
            collection=self.name,
            example_data=example_data
        )

        if result_dict['count'] > 0:
            for result in result_dict['result']:
                doc = Document(
                    id=result['_id'],
                    key=result['_key'],
                    collection=self.name,
                    api=self.api,
                )

                all_docs.append(doc)

        return all_docs

    def documents(self):
        """
        """

        document_list = []
        document_uri_list = self.api.document.get(collection=self.name)['documents']
        for document_uri in document_uri_list:
            splitted_uri = document_uri.split('/')
            document_key = splitted_uri[-1]
            document_id = "%s/%s" % (self.name, document_key)

            doc = Document(
                id=document_id,
                key=document_key,
                collection=self,
                api=self.api
            )
            document_list.append(doc)

        return document_list


class Document(object):

    @classmethod
    def create(cls, collection):
        """
        """

        api = Client.instance().api

        data = api.document.post(data={}, collection=collection.name)

        doc = Document(
            id=data['_id'],
            key=data['_key'],
            collection=collection.name,
            api=api,
        )

        doc.is_loaded = True

        return doc

    def __init__(self, id, key, collection, api):
        """
        """

        self.id = id
        self.key = key
        self.collection = collection
        self.api = api
        self.resource = api.document

        self.data = {}

        self.is_loaded = False

    def get(self):
        """
        """

        data = self.resource(self.id).get()
        self.data = data

        return data

    def save(self):
        """
        """

        self.resource(self.id).patch(data=self.data)

    def getData(self, key):
        """
        """

        if not self.is_loaded:
            self.get()

            self.is_loaded = True

        return self.data[key]

    def setData(self, key, value):
        """
        """

        self.data[key] = value

    def __repr__(self):
        """
        """
        return self.__str__()

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u"%s" % self.id


class Edge(Document):

    @classmethod
    def create(cls, collection, from_doc, to_doc, edge_data={}):
        """
        """

        api = Client.instance().api

        parameters = {
            'collection': collection.name,
            'from': from_doc.id,
            'to': to_doc.id,
        }

        try:
            data = api.edge.post(data=edge_data, **parameters)
        except Exception as err:
            print(err.content)
            raise err

        doc = Edge(
            id=data['_id'],
            key=data['_key'],
            collection=collection.name,
            api=api,
        )

        return doc

    def __init__(self, id, key, collection, api):
        """
        """

        super(Edge, self).__init__(id=id, key=key, collection=collection, api=api)

        self.resource = api.edge
