import abc
from ..compat import add_metaclass
from ..abc import DeletableResource
from ..abc import EditableResource
from ..abc import ViewableResource
from sqlalchemy.orm import object_session

_session_factory = None


@add_metaclass(abc.ABCMeta)
class SQLResource(DeletableResource, EditableResource, ViewableResource):
    """Base class for resources based on SQLAlchemy ORM models.
    """

    @abc.abstractproperty
    def context_query(self):
        """A SQLAlchemy query which is used to find a SQLAlchemy object.
        """
        raise NotImplemented()

    def __init__(self, request):
        global _session_factory
        assert _session_factory is not None, \
                "config.set_sqlalchemy_session_factory must be called."
        params = request.matchdict
        self.context = _session_factory.execute(self.context_query, params).first()
        if self.context is None:
            raise KeyError('Resource not found')

    def to_dict(self):
        data = {}
        columns = self.context_query._primary_entity.entity_zero.columns
        for column in columns:
            data[column] = getattr(self.context, column)
        return data

    def update_from_dict(self, data, partial=False):
        columns = self.context_query._primary_entity.entity_zero.columns
        for column in columns:
            if partial:
                setattr(self.context, column, data.get(column))
            else:
                setattr(self.context, column, data[column])

    def delete(self):
        object_session(self.context).delete(self.context)


def set_sqlalchemy_session_factory(config, sql_session_factory):
    """Configure the SQLAlchemy session factory.

    This function should not be used directly, but as a method if the
    ``config`` object.

    .. code-block:: python

       config.set_sqlalchemy_session_factory(DBSession)

    This function must be called if you use SQL resources. If you forget to do
    this any attempt to access a SQL resource will trigger an assertion
    exception.

    :param sql_session_factory: A factory function to return a SQLAlchemy
        session. This is generally a :ref:`scoped_session
        <sqlalchemy:sqlalchemy.orm.scoping.scoped_session>` instance, and
        commonly called ``Session`` or ``DBSession``.
    """
    global _session_factory
    _session_factory = sql_session_factory


def includeme(config):
    """Configure SQLAlchemy integration.

    You should not call this function directly, but use
    :py:func:`pyramid.config.Configurator.include` to initialise the REST
    toolkit. After you have done this you must call
    :py:func:`config.set_sqlalchemy_session_factory` to register your
    SQLALchemy session factory.

    .. code-block:: python

       config = Configurator()
       config.include('rest_toolkit')
       config.include('rest_toolkit.ext.sql')
       config.set_sqlalchemy_session_factory(DBSession)
    """
    config.add_directive('set_sqlalchemy_session_factory',
            set_sqlalchemy_session_factory)
