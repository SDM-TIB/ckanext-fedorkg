from ckan.model import meta
from ckan.model.domain_object import DomainObject
from sqlalchemy import Column, Table, types

news_table = Table(
    'fedorkg_news',
    meta.metadata,
    Column('identifier', types.UnicodeText, primary_key=True),
    Column('endpoint_url', types.UnicodeText, nullable=False),
    Column('notification_type', types.UnicodeText, nullable=True),
    Column('message', types.UnicodeText, nullable=False),
    Column('date', types.DateTime, nullable=False)
)


class News(DomainObject):
    """News object"""
    pass


meta.mapper(News, news_table)
