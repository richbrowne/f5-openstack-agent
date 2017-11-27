#!/usr/bin/env python
# Copyright 2017 F5 Networks Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import pytest

from mock import Mock

from f5_openstack_agent.lbaasv2.drivers.bigip import l7policy_adapter


@pytest.fixture
def conf():
    conf = Mock()
    conf.environment_prefix = "TEST"
    return conf


@pytest.fixture
def policy_adapter(conf):
    policy_adapter = l7policy_adapter.L7PolicyServiceAdapter(conf)

    return policy_adapter


def test_create_policy_adatper(policy_adapter):
    print policy_adapter
