# -*- coding: utf-8 -*-

import json
import unittest

import mock
import pytest

import talentlms


class TalentLMSTest(unittest.TestCase):
    def setUp(self):
        self.api = talentlms.api('example.talentlms.com', 'FAKE_API_KEY_HERE')
        self.test_data = {'param_1': 'str_value:with/special.symbols',
                          'param_2': 1,
                          'param_3': False,
                          'param_4': 'user@example.com'}

    @mock.patch('talentlms.requests.get')
    def test_get_success(self, mock_get):
        expected_return = {'result': 'ok'}
        expected_url = 'https://example.talentlms.com/api/v1/test_api_method/' + \
            'param_1:str_value%3Awith%2Fspecial.symbols,param_2:1,param_3:False,' + \
            'param_4:user@example.com'

        mock_get.return_value.ok = True
        mock_get.return_value.text = json.dumps(expected_return)

        response = self.api.get('test_api_method', self.test_data)

        mock_get.assert_called_with(expected_url, auth=self.api.auth)
        self.assertEqual(response, expected_return)

    @mock.patch('talentlms.requests.post')
    def test_post_success(self, mock_post):
        expected_return = {'result': 'ok'}
        expected_url = 'https://example.talentlms.com/api/v1/test_api_method'

        mock_post.return_value.ok = True
        mock_post.return_value.text = json.dumps(expected_return)

        response = self.api.post('test_api_method', self.test_data)

        mock_post.assert_called_with(expected_url, data=self.test_data, auth=self.api.auth)
        self.assertEqual(response, expected_return)

    @mock.patch('talentlms.requests.get')
    def test_custom_exception(self, mock_get):
        mock_get.return_value.ok = False
        mock_get.return_value.text = json.dumps({
            'error': {
                'type': 'invalid_request_error',
                'message': 'The requested user does not exist'
            }
        })

        with self.assertRaises(talentlms.UserDoesNotExistError):
            self.api.get('users', { 'id': 123456 })