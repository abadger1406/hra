from urllib import parse

import logging
import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.management import BaseCommand, CommandError
from django.utils.datetime_safe import date

from hra.research_summaries.importers import ResearchSummaryPageImporter
from hra.research_summaries.models import ResearchSummariesIndexPage


logger = logging.getLogger('hra.research_summaries')


class APIError(Exception):
    pass


# TODO: Create a separate module for fetch code
class Command(BaseCommand):
    def handle(self, *args, **options):
        parent_page = ResearchSummariesIndexPage.objects.first()

        if not parent_page:
            raise CommandError(
                "There is no ResearchSummariesIndexPage pages. "
                "You have to create one to be able to import research summaries."
            )

        # TODO: Use arguments
        start_date = date(2015, 12, 1)
        end_date = date(2015, 12, 31)

        api_url = getattr(settings, 'HARP_API_URL', None)
        api_username = getattr(settings, 'HARP_API_USERNAME', None)
        api_password = getattr(settings, 'HARP_API_PASSWORD', None)
        api_date_format = '%Y-%m-%d'

        if not all([api_url, api_username, api_password]):
            raise ImproperlyConfigured(
                "HARP API settings are incorrect. "
                "You must specify the following settings: "
                "HARP_API_URL, HARP_API_USERNAME and HARP_API_PASSWORD"
            )

        query_params = parse.urlencode({
            # Explicitly convert date into a string of required format
            'datePublishedFrom': start_date.strftime(api_date_format),
            'datePublishedTo': end_date.strftime(api_date_format),
        })

        request_url = '{}?{}'.format(api_url, query_params)
        response = requests.get(request_url, auth=(api_username, api_password))

        if response.status_code != 200:
            raise APIError(
                "Failed to fetch research summary data from '{}' (received '{} {}' response)".format(
                    request_url,
                    response.status_code,
                    response.reason,
                )
            )

        data = response.json()

        if not isinstance(data, list):
            raise APIError(
                "API has returned {}. Expected type: {}".format(type(data), list)
            )

        for item in data:
            importer = ResearchSummaryPageImporter(item)

            try:
                importer.create_or_update_page(parent_page)
            except (ValidationError, ValueError):
                logger.exception(
                    "Unable to create or update a page "
                    "due to validation errors. {}={}".format(
                        importer.id_mapping.source,
                        importer.id_mapping.get_field_data(item),
                    )
                )
