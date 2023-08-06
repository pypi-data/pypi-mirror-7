# -*- coding: utf8 -*-
""" This module provides some classes to simplify acces to OpenERP server via xmlrpc.
    Some of these classes are may be not safe enough and should be used with carefully

    Example ussage of this module:

    >>> erp_db = ERP_Proxy('dbname', 'server.com', 'some_user', 'mypassword')
    >>> sale_obj = erp_db['sale_order']
    >>> sale_ids = sale_obj.search([('state','not in',['done','cancel'])])
    >>> sale_data = sale_obj.read(sale_ids, ['name'])
    >>> for order in sale_data:
    ...     print "%5s :    %s" % (order['id'],order['name'])
    >>> tmpl_ids = erp_db['product.template'].search([('name','ilike','template_name')])
    >>> print erp_db['product.product'].search([('product_tmpl_id','in',tmpl_ids)])

    >>> db = ERP_Proxy(dbname='db0', 'erp.host.com', 'your_user')
    >>> so = db['sale.order']
    >>> order_ids = so.search([('state','=','done')])
    >>> order = so.read(order_ids[0])

    Also You can call any method (beside private ones starting with underscore(_)) of any model.
    For example to check availability of stock move all You need is:

    >>> db = session.connect()
    >>> move_obj = db['stock.move']
    >>> move_ids = [1234] # IDs of stock moves to be checked
    >>> move_obj.check_assign(move_ids)

    Ability to use ERP_Record class as analog to browse_record:

    >>> move_obj = db['stock.move']
    >>> move = move_obj.read_records(1234)
    >>> move.state
    ... 'confirmed'
    >>> move.check_assign()
    >>> move.refresh()
    >>> move.state
    ... 'assigned'
    >>> move.picking_id
    ... [12, 'OUT-12']
    >>> move.picking_id__obj.id
    ... 12
    >>> move.picking_id__obj.name
    ... 'OUT-12'
    >>> move.picking_id__obj.state
    ... 'assigned'
"""


import functools

# project imports
from openerp_proxy.connection import get_connector
from openerp_proxy.exceptions import Error, ConnectorError


__all__ = ('ERPProxyException', 'ERP_Proxy', 'ERP_Object', 'ERP_Record')


class ERPProxyException(Error):
    pass


class ERP_Proxy(object):
    """
       A simple class to connect ot ERP via xml_rpc
       Should be initialized with following arguments:

           >>> db = ERP_Proxy('dbname', 'host', 'user', pwd = 'Password', verbose = False)

       Allows access to ERP objects via dictionary syntax:

           >>> db['sale.order']
                ERP_Object: 'sale.order'

       TODO: describe methods and how to use them

    """

    def __init__(self, dbname, host, user, pwd, port=8069, protocol='xml-rpc', verbose=False):
        self.dbname = dbname
        self.host = host
        self.user = user
        self.port = port
        self.pwd = pwd
        self.verbose = verbose
        self.protocol = protocol

        self._connection = get_connector(protocol)(host, port, verbose=verbose)

        self.__objects = {}   # cached objects

        # properties
        self.__registered_objects = None

        self.__use_execute_kw = None

        self.uid = None

        # Connect to database
        self.connect()

    @property
    def registered_objects(self):
        """ Stores list of registered in ERP database objects
        """
        if self.__registered_objects is not None:
            return self.__registered_objects
        ids = self.execute('ir.model', 'search', [])
        read = self.execute('ir.model', 'read', ids, ['model'])
        self.__registered_objects = [x['model'] for x in read]
        return self.__registered_objects

    def get_service(self, name):
        return self._connection.get_service(name)

    def connect(self):
        """ Connects to the server

            returns Id of user connected
        """
        # Get the uid
        service_auth = self.get_service('common')
        self.uid = service_auth.login(self.dbname, self.user, self.pwd)

        if not self.uid:
            raise ERPProxyException("Bad login or password")

        return self.uid

    def reconnect(self):
        """ Recreates connection to the server and clears caches
        """
        self.connect()

    # Report related methods
    def report(self, report_name, ids, context):
        """ Proxy to report service *report* method

            @param report_name: string representing name of report service
            @param ids: list of object ID to get report for
            @param context: Ususaly have to have 'model' and 'id' keys that describes object to get report for
            @return: ID of report to get by method *report_get*
        """
        return self.get_service('report').report(self.dbname, self.uid, self.pwd, report_name, ids, context)

    def report_get(self, report_id):
        """ Proxy method to report servce *report_get* method

            @param report_id: int that represents ID of report to get
            @return: dictinary with keys:
                        - 'state': boolean, True if report generated correctly
                        - 'result': base64 encoded content of report
                        - 'format': string representing format, report generated in

        """
        return self.get_service('report').report_get(self.dbname, self.uid, self.pwd, report_id)

    # Object related methods
    def use_execute_kw(self):
        """ Checks whether 'execute_kw' method is available or not
        """
        if self.__use_execute_kw is None:
            service = self.get_service('object')
            try:
                service.execute_kw(self.dbname, self.uid, self.pwd, 'ir.model', 'search', ([],), dict(limit=1))
                self.__use_execute_kw = True
            except ConnectorError:
                self.__use_execute_kw = False
        return self.__use_execute_kw

    def execute(self, obj, method, *args, **kwargs):
        """First arguments should be 'object' and 'method' and next
           will be passed to method of given object
        """
        service = self.get_service('object')

        if self.use_execute_kw():
            result = service.execute_kw(self.dbname, self.uid, self.pwd, obj, method, args, kwargs)
        else:
            result = service.execute(self.dbname, self.uid, self.pwd, obj, method, *args, **kwargs)

        return result

    def execute_wkf(self, object_name, signal, object_id):
        """ Triggers workflow event on specified object
        """
        service = self.get_service('object')
        result_wkf = service.exec_workflow(self.dbname, self.uid, self.pwd, object_name, signal, object_id)
        return result_wkf

    def get_obj(self, object_name):
        """ Returns wraper around openERP object 'object_name' which is instance of ERP_Object

            @param object_name: name of an object to get wraper for
            @return: instance of ERP_Object which wraps choosen object
        """
        if object_name in self.__objects:
            return self.__objects[object_name]

        if object_name not in self.registered_objects:
            raise ValueError("There is no object named '%s' in ERP" % object_name)

        obj = ERP_Object(self, object_name)
        self.__objects[object_name] = obj
        return obj

    def __getitem__(self, name):
        """ Returns instance of ERP_Object with name 'name'
        """
        res = None
        try:
            res = self.get_obj(name)
        except ValueError:
            raise KeyError('Wrong object name')

        return res

    def get_url(self):
        return "%(protocol)s://%(user)s@%(host)s:%(port)s/%(database)s" % dict(user=self.user,
                                                                host=self.host,
                                                                database=self.dbname,
                                                                port=self.port,
                                                                protocol=self.protocol)

    def __str__(self):
        return "ERP_Proxy: %s" % self.get_url()
    __repr__ = __str__


def MethodWrapper(erp_proxy, object_name, method_name):
    """ Wraper around ERP objects's methods.

        for internal use.
        It is used in ERP_Object class.
    """
    def wrapper(*args, **kwargs):
        return erp_proxy.execute(object_name, method_name, *args, **kwargs)
    return wrapper


class ERP_Record(object):
    """ A simple class to wrap OpenERP records

        All fields could be used as dictionary items and as attributes of object
        All methods could be accessed as attibutes of class, and they will be automaticaly
        proxied to related ERP_Object instance passing as IDs [self.id]

        Special methods:

            - refresh() - rereads data for this object
            - workflow_trg(signal) - sends specified signal to record's
                                     workflow
    """

    # TODO: think about optimization via slots
    # TODO: add more doc on aditional functionality like using __obj suffix to
    # access related by many2one records

    def __init__(self, obj, data):
        assert isinstance(obj, ERP_Object), "obj should be ERP_Object"
        assert isinstance(data, dict), "data should be dictionary structure returned by ERP_Object.read"
        self.__obj = obj
        self.__data = data
        self.__related_objects = {}
        self.__workflow_instance = None

    def __dir__(self):
        res = dir(super(ERP_Record, self))
        res.extend(self.__data.keys())
        res.extend(['read', 'search', 'write', 'unlink', 'create'])
        return res

    def _get_obj(self):
        """ Returns instance of related ERP_Object
        """
        return self.__obj

    def _get_proxy(self):
        """ Returns instance of related ERP_Proxy object
        """
        return self.__obj._get_proxy()

    def _get_columns_info(self):
        """ Returns dictionary with information about columns of related object
        """
        return self.__obj._get_columns_info()

    def _get_workflow_instance(self):
        """ Retunrs workflow instance related to this record
        """
        if self.__workflow_instance is None:
            wkf = self.__obj._get_workflow()
            if not wkf:
                self.__workflow_instance = False
            else:
                wkf_inst_obj = self._get_proxy().get_obj('workflow.instance')
                wkf_inst_records = wkf_inst_obj.search_records([('wkf_id', '=', wkf.id),
                                                                ('res_id', '=', self.id)], limit=1)
                self.__workflow_instance = wkf_inst_records and wkf_inst_records[0] or False
        return self.__workflow_instance

    def _get_workflow_items(self):
        """ Returns list of related workflow.woritem objects
        """
        # TODO: think about adding caching
        workitem_obj = self._get_proxy().get_obj('workflow.workitem')
        wkf_inst = self._get_workflow_instance()
        if wkf_inst:
            return workitem_obj.search_records([('inst_id', '=', wkf_inst.id)])
        return []

    def __str__(self):
        return "ERP_Record (%s, %s)" % (self.__obj.name, self.id)
    __repr__ = __str__

    def __getattribute__(self, name):
        res = None
        try:
            res = super(ERP_Record, self).__getattribute__(name)
        except AttributeError:
            try:
                res = self[name]
            except KeyError:
                method = getattr(self.__obj, name)
                res = functools.partial(method, [self.id])
        return res

    def __get_many2one_rel_obj(self, name, cached=True):
        """ Method used to fetch related object by name of field that points to it
        """
        if name not in self.__related_objects or not cached:
            relation = self._get_columns_info()[name].relation
            rel_obj = self._get_proxy().get_obj(relation)
            rel_data = self[name]
            rel_id = rel_data and rel_data[0] or False  # Do not forged about relations in form [id, name]
            self.__related_objects[name] = rel_obj.read_records(rel_id)
        return self.__related_objects[name]

    def __get_one2many_rel_obj(self, name, cached=True, limit=None):
        """ Method used to fetch related objects by name of field that points to them
            using one2many relation
        """
        if name not in self.__related_objects or not cached:
            relation = self._get_columns_info()[name].relation
            rel_obj = self._get_proxy().get_obj(relation)
            rel_ids = self[name]   # Take in mind that field value is list of IDS
            self.__related_objects[name] = rel_obj.read_records(rel_ids)
        return self.__related_objects[name]

    def __get_related_field(self, name):
        """ Method to fetch related object's data
        """
        col_info = self._get_columns_info()[name]
        if col_info.ttype == 'many2one':
            return self.__get_many2one_rel_obj(name)
        elif col_info.ttype == 'one2many' or col_info.ttype == 'many2many':
            return self.__get_one2many_rel_obj(name)
        else:
            raise KeyError("There are no related field %s in model %s" % (name, self._get_obj().name))

    def __getitem__(self, name):
        # Allow using '__obj' suffix in field name to retrive ERP_Record
        # instance of object related via many2one or one2many or many2many
        # This means next:
        #    >>> o = db['sale.order.line'].read_records(1)
        #    >>> o.order_id
        #    ... [25, 'order_name']
        #    >>> o.order_id__obj
        #    ... ERP_Record of sale.order, 25
        if name.endswith('__obj'):
            fname = name[:-5]
            return self.__get_related_field(fname)
        else:
            return self.__data[name]

    def refresh(self):
        self.__data.update(self.__obj.read(self.id))

        # Update related objects cache
        self.__related_objects = {}

    def as_dict(self):
        return self.__data.copy()

    def workflow_trg(self, signal):
        """ trigger's specified signal on record's related workflow
        """
        return self._get_obj().workflow_trg(self.id, signal)


class ERP_Object(object):
    """ A simple class to simplify operations on ERP objects.
        It gives interface like open ERP osv.osv objects.

        Example:

        >>> erp = ERP_Proxy(...)
        >>> sale_obj = ERP_Object(erp, 'sale.order')
        >>> sale_obj.search([('state','not in',['done','cancel'])])

        Special methods:

            - search_records - receives same arguments as 'search' method,
                               but returns list of ERP_Record objects or False
            - read_records - receives same arguments as 'read', but returns
                             list of ERP_Record objects. Or if single int passed as IDs
                             it will returns single ERP_Record object
            - workflow_trg(id, signal) - sends specified signal to object with
                                         specified 'id'
    """

    # TODO: add doc on new methods ?
    def __init__(self, erp_proxy, object_name):
        self.__erp_proxy = erp_proxy
        self.__obj_name = object_name
        self.__columns_info = None
        self.__workflow = None

    @property
    def name(self):
        return self.__obj_name

    def _get_proxy(self):
        return self.__erp_proxy

    def __dir__(self):
        res = dir(super(ERP_Object, self))
        res.extend(['read', 'search', 'write', 'unlink', 'create'])
        return res

    def _get_columns_info(self):
        """ Reads information about fields available on model
        """
        if self.__columns_info is None:
            columns_info = {}
            fields_obj = self.__erp_proxy['ir.model.fields']
            fields = fields_obj.search_records([('model', '=', self.__obj_name)])
            for field in fields:
                columns_info[field.name] = field

            self.__columns_info = columns_info

        return self.__columns_info

    def _get_workflow(self):
        """ Returns ERP_Record instance of "workflow" object
            related to this ERP_Object

            If there are no workflow for an object then False will be returned
        """
        if self.__workflow is None:
            wkf_obj = self.__erp_proxy['workflow']
            # TODO: implement correct behavior for situations with few
            # workflows for same model.
            wkf_records = wkf_obj.search_records([('osv', '=', self.__obj_name)])
            if wkf_records and len(wkf_records) > 1:
                raise ERPProxyException("More then one workflow per model not supported "
                                        "be current version of openerp_proxy!")
            self.__workflow = wkf_records and wkf_records[0] or False
        return self.__workflow

    def search_records(self, *args, **kwargs):
        """ Return instance or list of instances of ERP_Record class,
            making available to work with data simpler:

                >>> so_obj = db['sale.order']
                >>> data = so_obj.search_records([('date','>=','2013-01-01')])
                >>> for order in data:
                        order.write({'note': 'order date is %s'%order.date})

            Additionally accepts keyword argument 'read_field' which can be used to specify
            list of fields to read
        """

        read_fields = kwargs.pop('read_fields', [])

        res = self.search(*args, **kwargs)
        if not res:
            return []

        if read_fields:
            return self.read_records(res, read_fields)
        return self.read_records(res)

    def read_records(self, ids, *args, **kwargs):
        """ Return instance or list of instances of ERP_Record class,
            making available to work with data simpler:

                >>> so_obj = db['sale.order']
                >>> data = so_obj.read_records([1,2,3,4,5])
                >>> for order in data:
                        order.write({'note': 'order data is %s'%order.data})
        """
        assert isinstance(ids, (int, long, list, tuple)), "ids must be instance of (int, long, list, tuple)"
        if isinstance(ids, (int, long)):
            return ERP_Record(self, self.read(ids, *args, **kwargs))
        if isinstance(ids, (list, tuple)):
            return [ERP_Record(self, data) for data in self.read(ids, *args, **kwargs)]

    def workflow_trg(self, obj_id, signal):
        """ Triggers specified signal for object's workflow
        """
        assert isinstance(obj_id, (int, long)), "obj_id must be integer"
        assert isinstance(signal, basestring), "signal must be string"
        return self._get_proxy().execute_wkf(self.__obj_name, signal, obj_id)

    def __getattribute__(self, name):
        res = None
        try:
            res = super(ERP_Object, self).__getattribute__(name)
        except AttributeError:
            res = MethodWrapper(self.__erp_proxy, self.__obj_name, name)

        return res

    def __str__(self):
        return "ERP Object ('%s')" % self.__obj_name
    __repr__ = __str__
