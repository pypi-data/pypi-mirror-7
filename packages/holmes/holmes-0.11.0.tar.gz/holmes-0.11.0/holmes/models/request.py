#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlalchemy as sa
from sqlalchemy import func
from datetime import date, datetime, timedelta

from holmes.utils import get_status_code_title
from holmes.models import Base


class Request(Base):
    __tablename__ = "requests"

    id = sa.Column(sa.Integer, primary_key=True)
    domain_name = sa.Column('domain_name', sa.String(120), nullable=False)
    url = sa.Column('url', sa.Text(), nullable=False)
    effective_url = sa.Column('effective_url', sa.Text(), nullable=False)
    status_code = sa.Column('status_code', sa.Integer, nullable=False)
    response_time = sa.Column('response_time', sa.Float, nullable=False)
    completed_date = sa.Column('completed_date', sa.Date, nullable=False)
    review_url = sa.Column('review_url', sa.Text(), nullable=False)

    def to_dict(self):
        return {
            'domain_name': str(self.domain_name),
            'url': self.url,
            'effective_url': self.effective_url,
            'status_code': self.status_code,
            'response_time': self.response_time,
            'completed_date': self.completed_date,
            'review_url': self.review_url
        }

    def __str__(self):
        return "%s (%s)" % (self.url, self.status_code)

    def __repr__(self):
        return str(self)

    @classmethod
    def get_status_code_info(self, domain_name, db):
        result = []

        query = db \
            .query(
                Request.status_code,
                sa.func.count(Request.status_code).label('total')
            ) \
            .filter(Request.domain_name == domain_name) \
            .group_by(Request.status_code) \
            .all()

        for i in query:
            result.append({
                'code': i.status_code,
                'title': get_status_code_title(i.status_code),
                'total': i.total
            })

        return result

    @classmethod
    def get_requests_by_status_code(self, domain_name, status_code, db, current_page=1, page_size=10):
        lower_bound = (current_page - 1) * page_size
        upper_bound = lower_bound + page_size

        requests = db \
            .query(Request.id, Request.url, Request.review_url, Request.completed_date) \
            .filter(Request.domain_name == domain_name) \
            .filter(Request.status_code == status_code) \
            .order_by('completed_date desc')[lower_bound:upper_bound]

        return requests

    @classmethod
    def get_requests_by_status_count(self, domain_name, status_code, db):
        return db \
            .query(func.count(Request.id)) \
            .filter(Request.domain_name == domain_name) \
            .filter(Request.status_code == status_code) \
            .scalar()

    @classmethod
    def get_last_requests(self, db, current_page=1, page_size=10,
                          domain_filter=None):
        lower_bound = (current_page - 1) * page_size
        upper_bound = lower_bound + page_size

        query = db.query(Request)

        if domain_filter:
            from holmes.models.domain import Domain
            domain = Domain.get_domain_by_name(domain_filter, db)
            if domain:
                query = query.filter(Request.domain_name == domain.name)

        return query.order_by('id desc')[lower_bound:upper_bound]

    @classmethod
    def get_requests_count_by_status_in_period_of_days(self, db, from_date, to_date=None):
        if to_date is None:
            to_date = datetime.utcnow()

        return db \
            .query(Request.status_code, sa.func.count(Request.id).label('count')) \
            .filter(Request.completed_date.between(from_date.date(), to_date.date())) \
            .group_by(Request.status_code) \
            .order_by('count DESC') \
            .all()

    @classmethod
    def delete_old_requests(self, db, config, limit=1000):
        dt = date.today() - timedelta(days=config.DAYS_TO_KEEP_REQUESTS)

        older_requests = db \
            .query(Request) \
            .filter(Request.completed_date <= dt) \
            .limit(limit) \

        older_requests_ids = [item.id for item in older_requests]

        return db \
            .query(Request) \
            .filter(Request.id.in_(older_requests_ids)) \
            .delete(synchronize_session=False)
