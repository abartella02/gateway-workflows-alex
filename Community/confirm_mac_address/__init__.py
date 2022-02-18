# Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates
# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# By: BlueCat Networks
# Date: 2019-03-14
# Gateway Version: 18.10.2
# Description: Register MAC Address init

type = 'ui'
sub_pages = [
    {
        'name'        : 'confirm_mac_address_page',
        'title'       : "MAC Address Confirmation",
        'endpoint'    : 'confirm_mac_address/confirm_mac_address_endpoint',
        'description' : "To confirm if MAC address is registered"
    },
]
