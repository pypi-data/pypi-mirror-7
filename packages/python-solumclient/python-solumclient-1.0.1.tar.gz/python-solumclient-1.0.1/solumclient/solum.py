# Copyright (c) 2014 Rackspace
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Initial M1 Solum CLI commands implemented (but not REST communications):
* app create --repo="repo_url" [--build=no] plan_name
* app delete plan_name
* app list
* app show plan_id
* assembly create [--assembly="assembly_name"] plan_name
* assembly delete assembly_name
* assembly list
* assembly show assembly_id
* languagepack create lp_file
* languagepack list
* languagepack show lp_id
* languagepack delete lp_id


Notes:
* This code is expected to be replaced by the OpenStack Client (OSC) when
    it has progressed a little bit farther as described at:
    https://wiki.openstack.org/wiki/Solum/CLI
* Internationalization will not be added in M1 since this is a prototype
"""

from __future__ import print_function

import argparse
import json
import sys

import six
import yaml

from solumclient.common import cli_utils
from solumclient.openstack.common import cliutils
from solumclient.openstack.common import strutils
from solumclient.v1 import assembly as cli_assem
from solumclient.v1 import plan as cli_plan


class AppCommands(cli_utils.CommandsBase):
    """Application targets."""

    def create(self):
        """Create an application."""
        self.parser.add_argument('plan_file',
                                 help="Plan file")
        args = self.parser.parse_args()
        with open(args.plan_file) as definition_file:
            definition = definition_file.read()

        # Convert yaml to json until we add yaml support in API layer.
        try:
            data = yaml.load(definition)
        except yaml.YAMLError as exc:
            print("Error in plan file: %s", str(exc))
            sys.exit(1)

        plan = self.client.plans.create(**data)

        fields = ['uuid', 'name', 'description', 'uri']
        data = dict([(f, getattr(plan, f, ''))
                     for f in fields])
        cliutils.print_dict(data, wrap=72)

    def delete(self):
        """Delete an application."""
        self.parser.add_argument('plan_uuid',
                                 help="Tenant/project-wide unique "
                                 "plan uuid or name")
        args = self.parser.parse_args()
        plan = self.client.plans.find(name_or_id=args.plan_uuid)
        cli_plan.PlanManager(self.client).delete(plan_id=str(plan.uuid))

    def show(self):
        """Show an application's resource."""
        self.parser.add_argument('plan_uuid',
                                 help="Plan uuid or name")
        args = self.parser.parse_args()
        response = self.client.plans.find(name_or_id=args.plan_uuid)
        fields = ['uuid', 'name', 'description', 'uri']
        data = dict([(f, getattr(response, f, ''))
                     for f in fields])
        cliutils.print_dict(data, wrap=72)

    def list(self):
        """List all applications."""
        fields = ['uuid', 'name', 'description']
        response = self.client.plans.list()
        cliutils.print_list(response, fields)


class AssemblyCommands(cli_utils.CommandsBase):
    """Assembly targets."""

    def create(self):
        """Create an assembly."""
        self.parser.add_argument('plan_uri',
                                 help="Tenant/project-wide unique "
                                 "plan (uri/uuid or name)")
        self.parser.add_argument('--assembly',
                                 help="Assembly name")
        args = self.parser.parse_args()
        plan_uri = args.plan_uri
        if '/' not in plan_uri:
            # might be a plan uuid/name
            # let's try and be helpful and get the real plan_uri.
            plan = self.client.plans.find(name_or_id=args.plan_uri)
            plan_uri = plan.uri
            print('Note: using plan_uri=%s' % plan_uri)

        assembly = self.client.assemblies.create(name=args.assembly,
                                                 plan_uri=plan_uri)
        fields = ['uuid', 'name', 'description', 'status', 'application_uri',
                  'trigger_uri']
        data = dict([(f, getattr(assembly, f, ''))
                     for f in fields])
        cliutils.print_dict(data, wrap=72)

    def delete(self):
        """Delete an assembly."""
        self.parser.add_argument('assembly_uuid',
                                 help="Assembly uuid or name")
        args = self.parser.parse_args()
        assem = self.client.assemblies.find(name_or_id=args.assembly_uuid)
        cli_assem.AssemblyManager(self.client).delete(assembly_id=
                                                      str(assem.uuid))

    def list(self):
        """List all assemblies."""
        fields = ['uuid', 'name', 'description', 'status']
        response = self.client.assemblies.list()
        cliutils.print_list(response, fields)

    def show(self):
        """Show an assembly's resource."""
        self.parser.add_argument('assembly_uuid',
                                 help="Assembly uuid or name")
        args = self.parser.parse_args()
        response = self.client.assemblies.find(name_or_id=args.assembly_uuid)
        fields = ['uuid', 'name', 'description', 'status', 'application_uri',
                  'trigger_uri']
        data = dict([(f, getattr(response, f, ''))
                     for f in fields])
        cliutils.print_dict(data, wrap=72)


class LanguagePackCommands(cli_utils.CommandsBase):
    """Language Pack targets."""

    def create(self):
        """Create a language pack."""
        self.parser.add_argument('lp_file',
                                 help="Language pack file.")
        args = self.parser.parse_args()
        with open(args.lp_file) as lang_pack_file:
            try:
                data = json.load(lang_pack_file)
            except ValueError as exc:
                print("Error in language pack file: %s", str(exc))
                sys.exit(1)

        json_data = json.dumps(data)
        languagepack = self.client.languagepacks.create(json_data)
        fields = ['uuid', 'name', 'description', 'compiler_versions',
                  'os_platform']
        data = dict([(f, getattr(languagepack, f, ''))
                     for f in fields])
        cliutils.print_dict(data, wrap=72)

    def delete(self):
        """Delete a language pack."""
        self.parser.add_argument('lp_id',
                                 help="Language pack id")
        args = self.parser.parse_args()
        self.client.languagepacks.delete(lp_id=args.lp_id)

    def list(self):
        """List all language packs."""
        fields = ['uuid', 'name', 'description', 'compiler_versions',
                  'os_platform']
        response = self.client.languagepacks.list()
        cliutils.print_list(response, fields)

    def show(self):
        """Get a language pack."""
        self.parser.add_argument('lp_id',
                                 help="Language pack id")
        args = self.parser.parse_args()
        response = self.client.languagepacks.get(lp_id=args.lp_id)
        fields = ['uuid', 'name', 'description', 'compiler_versions',
                  'os_platform']
        data = dict([(f, getattr(response, f, ''))
                     for f in fields])
        cliutils.print_dict(data, wrap=72)


def main():
    """Basically the entry point."""
    parser = argparse.ArgumentParser(conflict_handler='resolve')
    parser.the_error = parser.error
    parser.error = lambda m: None

    resources = {
        'app': AppCommands,
        'assembly': AssemblyCommands,
        'languagepack': LanguagePackCommands
    }

    choices = resources.keys()

    parser.add_argument('resource', choices=choices,
                        help="Target noun to act upon")

    resource = None
    try:
        parsed, _ = parser.parse_known_args()
        resource = parsed.resource
    except Exception:
        print("Invalid target specified to act upon.\n")
        parser.print_help()
        sys.exit(1)

    if resource in resources:
        try:
            resources[resource](parser)
        except Exception as e:
            print(strutils.safe_encode(six.text_type(e)), file=sys.stderr)
            sys.exit(1)

    else:
        cli_utils.show_help(resources)
        print("\n")
        parser.print_help()

if __name__ == '__main__':
    sys.exit(main())
