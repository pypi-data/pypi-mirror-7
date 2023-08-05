#!/usr/bin/python
# -*- coding: utf-8 -*-

from holmes.validators.base import Validator
from holmes.facters.links import REMOVE_HASH


class AnchorWithoutAnyTextValidator(Validator):
    @classmethod
    def get_empty_anchors_message(cls, value):
        return 'Empty anchors are not good for Search Engines. ' \
               'Empty anchors were found for links to: %s.' % (
                   ', '.join([
                       '<a href="%s" target="_blank">#%s</a>' % (href, index)
                       for index, href in enumerate(value)
                   ]))

    @classmethod
    def get_violation_definitions(cls):
        return {
            'empty.anchors': {
                'title': 'Empty anchor(s) found',
                'description': cls.get_empty_anchors_message,
                'category': 'SEO'
            }
        }

    def validate(self):
        links = self.get_links()

        links_with_empty_anchor = []

        for link in links:
            href = link.get('href').strip()
            href = REMOVE_HASH.sub('', href)

            if href and not link.text_content() and not link.findall('img'):
                href = self.normalize_url(href)
                if not href:
                    continue
                links_with_empty_anchor.append(href)

        if links_with_empty_anchor:
            self.add_violation(
                key='empty.anchors',
                value=links_with_empty_anchor,
                points=20 * len(links_with_empty_anchor)
            )

    def get_links(self):
        return self.review.data.get('page.all_links', None)
