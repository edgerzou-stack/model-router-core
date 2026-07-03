import unittest
from unittest.mock import patch

import requests

from model_router.providers.openai_provider import OpenAIProvider
from model_router.exceptions import ProviderRequestError


class ProviderErrorTests(unittest.TestCase):
    @patch('model_router.providers.openai_provider.requests.post')
    def test_openai_provider_wraps_request_error(self, mock_post) -> None:
        response = requests.Response()
        response.status_code = 400
        response._content = b'{"error":"bad request"}'
        err = requests.HTTPError('400 Client Error', response=response)
        mock_post.side_effect = err
        provider = OpenAIProvider('OPENAI_API_KEY', 'https://example.com/v1', 'responses')
        with patch('os.getenv', return_value='token'):
            with self.assertRaises(ProviderRequestError) as ctx:
                provider.generate('hello', 'gpt-test')
        self.assertEqual(ctx.exception.provider, 'openai')
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn('bad request', ctx.exception.response_excerpt)
