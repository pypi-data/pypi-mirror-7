# Copyright 2013 - Noorul Islam K M
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from solumclient.openstack.common.apiclient import fake_client
from solumclient.tests import base
from solumclient.v1 import client as sclient
from solumclient.v1 import plan


plan_list = [
    {
        'uri': 'http://example.com/v1/plans/p1',
        'name': 'Example plan 1',
        'type': 'plan',
        'tags': ['small'],
        'artifacts': (
            [{'name': 'My python app',
              'artifact_type': 'git_pull',
              'content': {'href': 'git://example.com/project.git'},
              'requirements': [{
                  'requirement_type': 'git_pull',
                  'language_pack': '1dae5a09ef2b4d8cbf3594b0eb4f6b94',
                  'fulfillment': '1dae5a09ef2b4d8cbf3594b0eb4f6b94'}]}]),
        'services': [{'name': 'Build Service',
                      'id': 'build',
                      'characteristics': ['python_build_service']}],
        'project_id': '1dae5a09ef2b4d8cbf3594b0eb4f6b94',
        'user_id': '55f41cf46df74320b9486a35f5d28a11',
        'description': 'A plan with no services or artifacts shown'
    },
    {
        'uri': 'http://example.com/v1/plans/p2',
        'name': 'Example plan 2',
        'type': 'plan',
        'tags': ['small'],
        'artifacts': (
            [{'name': 'My java app',
              'artifact_type': 'git_pull',
              'content': {'href': 'git://example.com/project.git'},
              'requirements': [{
                  'requirement_type': 'git_pull',
                  'language_pack': '1dae5a09ef2b4d8cbf3594b0eb4f6b94',
                  'fulfillment': '1dae5a09ef2b4d8cbf3594b0eb4f6b94'}]}]),
        'services': [{'name': 'Build Service',
                      'id': 'build',
                      'characteristics': ['python_build_service']}],
        'project_id': '1dae5a09ef2b4d8cbf3594b0eb4f6b94',
        'user_id': '55f41cf46df74320b9486a35f5d28a11',
        'description': 'A plan with no services or artifacts shown'
    },
]

artifacts = [{'name': 'My python app',
              'artifact_type': 'git_pull',
              'content': {'href': 'git://example.com/project.git'},
              'requirements': [{
                  'requirement_type': 'git_pull',
                  'language_pack': '1dae5a09ef2b4d8cbf3594b0eb4f6b94',
                  'fulfillment': '1dae5a09ef2b4d8cbf3594b0eb4f6b94'}]}]

services = [{'name': 'Build Service',
             'id': 'build',
             'characteristics': ['python_build_service']}]

plan_fixture = {
    'uri': 'http://example.com/v1/plans/p1',
    'name': 'Example plan',
    'type': 'plan',
    'tags': ['small'],
    'artifacts': artifacts,
    'services': services,
    'project_id': '1dae5a09ef2b4d8cbf3594b0eb4f6b94',
    'user_id': '55f41cf46df74320b9486a35f5d28a11',
    'description': 'A plan with no services or artifacts shown'
}

plan_file_fixture = (
    '{"artifacts": [{"artifact_type": "application.heroku", '
    '"content": {"href": "http://github.com/some/project"}, '
    '"name": "My Python App", "language-pack": "language-pack-id"}], '
    '"name": "My Python App"}')

fixtures_list = {
    '/v1/plans': {
        'GET': (
            {},
            plan_list
        ),
    }
}


fixtures_get = {
    '/v1/plans/p1': {
        'GET': (
            {},
            plan_fixture
        ),
    }
}


fixtures_create = {
    '/v1/plans': {
        'POST': (
            {},
            plan_fixture
        ),
    }
}

fixtures_put = {
    '/v1/plans/p1': {
        'PUT': (
            {},
            plan_fixture
        ),
    }
}


class PlanManagerTest(base.TestCase):

    def assert_plan_obj(self, plan_obj):
        self.assertIn('Plan', repr(plan_obj))
        self.assertIn('Artifact', repr(plan_obj.artifacts[0]))
        self.assertIn('ServiceReference', repr(plan_obj.services[0]))
        self.assertEqual(plan_fixture['uri'], plan_obj.uri)
        self.assertEqual(plan_fixture['type'], plan_obj.type)
        self.assertEqual(plan_fixture['project_id'], plan_obj.project_id)
        self.assertEqual(plan_fixture['user_id'], plan_obj.user_id)

    def test_list_all(self):
        fake_http_client = fake_client.FakeHTTPClient(fixtures=fixtures_list)
        api_client = sclient.Client(fake_http_client)
        mgr = plan.PlanManager(api_client)
        plans = mgr.list()
        self.assertEqual(2, len(plans))
        self.assertIn('Plan', repr(plans[0]))
        self.assertIn('Artifact', repr(plans[0].artifacts[0]))
        self.assertIn('ServiceReference', repr(plans[0].services[0]))
        self.assertEqual(plan_list[0]['uri'], plans[0].uri)
        self.assertEqual(plan_list[1]['uri'], plans[1].uri)

    def test_create(self):
        fake_http_client = fake_client.FakeHTTPClient(fixtures=fixtures_create)
        api_client = sclient.Client(fake_http_client)
        mgr = plan.PlanManager(api_client)
        plan_obj = mgr.create(**plan_fixture)
        self.assert_plan_obj(plan_obj)

    def test_get(self):
        fake_http_client = fake_client.FakeHTTPClient(fixtures=fixtures_get)
        api_client = sclient.Client(fake_http_client)
        mgr = plan.PlanManager(api_client)
        plan_obj = mgr.get(plan_id='p1')
        self.assert_plan_obj(plan_obj)

    def test_update(self):
        fake_http_client = fake_client.FakeHTTPClient(fixtures=fixtures_put)
        api_client = sclient.Client(fake_http_client)
        mgr = plan.PlanManager(api_client)
        plan_obj = mgr.update(plan_id='p1', **plan_fixture)
        self.assert_plan_obj(plan_obj)
