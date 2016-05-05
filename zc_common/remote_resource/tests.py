import json

from django.test import TestCase
from rest_framework.test import APITestCase


class ResponseTestCase(APITestCase):
    SUCCESS_HIGH_LEVEL_KEYS = ['data']
    SUCCESS_DATA_KEYS = ['id', 'type']

    FAILURE_HIGH_LEVEL_KEYS = ['errors']
    FAILURE_DATA_KEYS = ['status', 'source', 'detail']

    def convert_to_list(self, data):
        if isinstance(data, list):
            return data
        else:
            return [data]

    def success_response_structure_test(self, response, status, relationship_keys=None):
        """
        This can be extended in the future to cover stricter validation of the
        response as follows:

        * Top level response MUST contain AT LEAST ONE of ['data', 'meta']
        * Top level response MUST contain ['links']  # Our requirement
            - Top level links MUST contain ['self']; MAY contain ['related']

        * Resource object MUST contain ['id', 'type']
        * Resource object MUST contain AT LEAST ONE of ['attributes', 'relationships']
        * Resource object MAY contain ['links', 'meta']

        * Relatiionship object MUST contain AT LEAST ONE of ['links', 'data', 'meta']
            - Relationship links object MUST contain AT LEAST ONE of ['self', 'related']
        """
        self.assertEqual(response.status_code, status)

        response_content = self.load_json(response)

        self.assertTrue(all(key in response_content for key in self.SUCCESS_HIGH_LEVEL_KEYS))

        for data in self.convert_to_list(response_content['data']):
            self.assertTrue(all(key in data for key in self.SUCCESS_DATA_KEYS))

            if relationship_keys:
                self.assertTrue('relationships' in data)
                relationships = data['relationships']
                self.assertTrue(all(key in relationships for key in relationship_keys))

                for relationship_name, relationship in relationships.iteritems():
                    self.assertTrue(all(key in relationship for key in ['data', 'meta']))

                    for relationship_data in self.convert_to_list(relationship['data']):
                        self.assertTrue(all(key in relationship_data for key in ['type', 'id']))

    def failure_response_structure_test(self, response, status):
        self.assertEqual(response.status_code, status)

        response_content = self.load_json(response)

        self.assertTrue(all(key in response_content for key in self.FAILURE_HIGH_LEVEL_KEYS))

        for error in response_content['errors']:
            self.assertTrue(all(key in error for key in self.FAILURE_DATA_KEYS))

    def load_json(self, response):
        return json.loads(response.content.decode())
