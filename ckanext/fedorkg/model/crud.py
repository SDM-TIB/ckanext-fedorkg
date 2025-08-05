from datetime import datetime as dt

from ckan.model import Session
from ckanext.fedorkg.model.news import News, news_table


class NewsQuery:
    cols = [c.name for c in news_table.c]

    @classmethod
    def create(cls, identifier, endpoint_url, notification_type, message, date=None):
        new_record = News(
            identifier=identifier,
            endpoint_url=endpoint_url,
            notification_type=notification_type,
            message=message,
            date=date if date is not None else dt.now()
        )
        Session.add(new_record)
        Session.commit()
        return new_record

    @classmethod
    def read_news(cls, identifier):
        return Session.query(News).get(identifier)

    @classmethod
    def read_all_news(cls):
        return Session.query(News).order_by(News.date.desc()).all()

    @classmethod
    def delete_news(cls, identifier):
        to_delete = cls.read_news(identifier)
        if to_delete is not None:
            Session.delete(to_delete)
            Session.commit()
            return True
        else:
            return False
