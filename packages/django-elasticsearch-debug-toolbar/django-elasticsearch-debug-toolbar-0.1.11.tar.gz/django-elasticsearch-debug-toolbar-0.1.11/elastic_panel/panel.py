from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from debug_toolbar.panels import Panel
from debug_toolbar.utils import ThreadCollector
import json

from elasticsearch.connection.base import Connection
#Patching og the orginal elasticsearch log_request
old_log_request_success = Connection.log_request_success
collector = ThreadCollector()

def patched_log_request_success(self, method, full_url, path, body, status_code, response, duration):
    collector.collect(ElasticQueryInfo(method, full_url, path, body, status_code, response, duration))
    old_log_request_success(self, method, full_url, path, body, status_code, response, duration)

Connection.log_request_success = patched_log_request_success

def _pretty_json(data):
    # pretty JSON in tracer curl logs
    try:
        return json.dumps(json.loads(data), sort_keys=True, indent=2, separators=(',', ': ')).replace("'", r'\u0027')
    except (ValueError, TypeError):
        # non-json data or a bulk request
        return data

class ElasticQueryInfo():
    def __init__(self, method, full_url, path, body, status_code, response, duration):
        self.method = method
        self.full_url = full_url
        self.path = path
        self.body = _pretty_json(body)
        self.status_code = status_code
        self.response = _pretty_json(response)
        self.duration = round(duration * 1000, 2)


class ElasticDebugPanel(Panel):
    """
    Panel that displays queries made by Elasticsearch backends.
    """
    name = 'Elasticsearch'
    template = 'elastic_panel/elastic_panel.html'
    has_content = True

    def nav_title(self):
        return _('Elastic Queries')

    def nav_subtitle(self):
        return "{} queries {}ms".format(self.nb_queries, self.total_time)

    def url(self):
        return ''

    def title(self):
        return self.nav_title()

    def process_request(self, request):
        collector.clear_collection()

    def process_response(self, request, response):
        records = collector.get_collection()
        self.total_time = 0

        for record in records:
            self.total_time += record.duration

        self.nb_queries = len(records)

        collector.clear_collection()
        self.record_stats({'records': records})