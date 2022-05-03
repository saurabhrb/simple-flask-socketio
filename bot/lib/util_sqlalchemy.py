import datetime
import pytz

from sqlalchemy.schema import DropTable
from sqlalchemy.ext.compiler import compiles
from sqlalchemy import DateTime, select, func, desc
from sqlalchemy.types import TypeDecorator

from bot.lib.util_datetime import tzware_datetime
from bot.lib.util_str import is_empty

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    
class AwareDateTime(TypeDecorator):
    """
    A DateTime type which can only store tz-aware DateTimes.

    Source:
      https://gist.github.com/inklesspen/90b554c864b99340747e
    """
    impl = DateTime(timezone=True)

    def process_bind_param(self, value, dialect):
        if isinstance(value, datetime.datetime) and value.tzinfo is None:
            raise ValueError('{!r} must be TZ-aware'.format(value))
        return value

    def __repr__(self):
        return 'AwareDateTime()'


def get_resource_mixin(db):

    @compiles(DropTable, "postgresql")
    def _compile_drop_table(element, compiler, **kwargs):
        return compiler.visit_drop_table(element) + " CASCADE"
        
    class ResourceMixin:
        created_on = db.Column(AwareDateTime(), default=tzware_datetime)
        updated_on = db.Column(AwareDateTime(), default=tzware_datetime, onupdate=tzware_datetime)

        @classmethod
        def sort_by(cls, field, direction):
            """
            Validate the sort field and direction.

            :param field: Field name
            :type field: str
            :param direction: Direction
            :type direction: str
            :return: tuple
            """
            if field not in cls.__table__.columns:
                field = 'created_on'

            if direction not in ('asc', 'desc'):
                direction = 'asc'

            return field, direction

        @classmethod
        def get_bulk_action_ids(cls, scope, ids, omit_ids=[], query=''):
            """
            Determine which IDs are to be modified.

            :param scope: Affect all or only a subset of items
            :type scope: str
            :param ids: List of ids to be modified
            :type ids: list
            :param omit_ids: Remove 1 or more IDs from the list
            :type omit_ids: list
            :param query: Search query (if applicable)
            :type query: str
            :return: list
            """
            omit_ids = map(str, omit_ids)

            if scope == 'all_search_results':
                # Change the scope to go from selected ids to all search results.
                ids = cls.query.with_entities(cls.id).filter(cls.search(query))

                # SQLAlchemy returns back a list of tuples, we want a list of strs.
                ids = [str(item[0]) for item in ids]

            # Remove 1 or more items from the list, this could be useful in spots
            # where you may want to protect the current user from deleting themself
            # when bulk deleting user accounts.
            if omit_ids:
                ids = [id for id in ids if id not in omit_ids]

            return ids

        @classmethod
        def bulk_delete(cls, ids):
            """
            Delete 1 or more model instances.

            :param ids: List of ids to be deleted
            :type ids: list
            :return: Number of deleted instances
            """
            delete_count = cls.query.filter(cls.id.in_(ids)).delete(
                synchronize_session=False)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e
            return delete_count

        def add(self):
            """
            Adds the model instance. (Doesn't commit to db yet)
            """
            db.session.add(self)

        def remove(self):
            """
            Removes the model instance. (Doesn't commit to db yet)
            """
            db.session.delete(self)

        # TODO: Remove this later
        def flush(self):
            """
            Saves changes in memory (ie id is assigned to the newly added record) but the database is not yet changed
            """
            db.session.flush()

        # Remove this later
        def commit(self):
            """
            Save changes to database permanently
            """
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e

        def save(self):
            """
            Adds the model and commits it to database.
            Equivalent of doing self.add() then self.commit()

            :return: Model instance
            """
            db.session.add(self)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e
            return self

        def delete(self):
            """
            Delete a model instance.
            Equivalent of doing self.remove() then self.commit()

            :return: db.session.commit()'s result
            """
            db.session.delete(self)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e

        @classmethod
        def last_record(cls):
            """
            Returns the highest id (as per the sorting order default on the id col)
            """
            return cls.query.order_by(cls.id.desc()).first()

        @classmethod
        def get_current_timestamp(cls):
            return db.session.execute(select([func.current_timestamp()])).first()[0]

        @classmethod
        def get_formatted_timestamp(cls, ):
            now = cls.get_current_timestamp()
            date = now.strftime("%Y.%m.%d")
            time = now.strftime("%H.%M.%S.%f")[:-5]
            result = f"{date}.{time}"
            return result

        def __str__(self):
            """
            Create a human readable version of a class instance.

            :return: self
            """
            obj_id = hex(id(self))
            columns = self.__table__.c.keys()

            values = ', '.join("%s=%r" % (n, getattr(self, n)) for n in columns)
            return '<%s %s(%s)>' % (obj_id, self.__class__.__name__, values)

    return ResourceMixin


def get_address_mixin(db, street_null=False, city_null=False, state_null=False, country_null=False, pincode_null=False):
    class AddressMixin:
        country_code = db.Column('country_code', db.String(10), nullable=country_null)
        country = db.Column('country', db.String(128), nullable=country_null)

        state_code = db.Column('state_code', db.String(10), nullable=state_null)
        state = db.Column('state', db.String(128), nullable=state_null)

        city = db.Column('city', db.String(128), nullable=city_null)
        pincode = db.Column('pincode', db.String(10), nullable=pincode_null)
        street = db.Column('street', db.String(255), nullable=street_null)

    return AddressMixin

