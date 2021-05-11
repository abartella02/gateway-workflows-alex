# Copyright 2021 BlueCat Networks (USA) Inc. and its affiliates
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
# Gateway Version: 20.12.1
# Description: Bulk Register Group Form

import os

from wtforms import FileField

from bluecat import util
import config.default_config as config

from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import CustomSubmitField
from bluecat.wtform_fields import TableField

def module_path():
    return os.path.dirname(os.path.abspath(str(__file__)))

def get_resource_text():
    return util.get_text(module_path(), config.language)

def table_features():
    """Returns table formatted data for display in the TableField component"""
    # pylint: disable=unused-argument
    text = get_resource_text()
    return {
        "columns": [
            {"title": text['title_group_name']},
            {"title": text['title_division_code']},
            {"title": text['title_comments']},
        ],
        "columnDefs": [
            {"width": "40%", "targets": [0]},
            {"width": "30%", "targets": [1]},
            {"width": "30%", "targets": [2]},
        ],
        'searching': False,
        'ordering': False,
        'info': False,
        'lengthChange': False,
        "data": []
    }


class GenericFormTemplate(GatewayForm):
    workflow_name = 'bulk_register_group'
    workflow_permission = 'bulk_register_group_page'
    
    text = get_resource_text()

    file = FileField(text['label_file'])
    group_list = TableField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label=text['label_list'],
        table_features=table_features(),
        buttons=[],
        is_disabled_on_start=False
    )

    submit = CustomSubmitField(
        label=text['label_submit'],
        is_disabled_on_start=True,
        is_disabled_on_error=True
    )
