# Copyright 2020 BlueCat Networks (USA) Inc. and its affiliates. All Rights Reserved.
"""
Workflow form template
"""
import datetime

from wtforms import StringField, PasswordField, FileField
from wtforms import BooleanField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Email, MacAddress, URL
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import Configuration, CustomStringField, IP4Address


class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'Nitrogen'
    workflow_permission = 'Nitrogen_page'
    configuration = Configuration(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Configuration',
        required=True,
        coerce=int,
        validators=[],
        is_disabled_on_start=False,
        on_complete=[],
        enable_on_complete=['email', 'password', 'ip_address'],
        clear_below_on_change=False
    )

    email = CustomStringField(
        label='Email',
        default='e@e.com',
        validators=[DataRequired(), Email()]
    )

    password = PasswordField(
        label='Password',
        default='abc',
        validators=[DataRequired()]
    )

    ip_address = IP4Address(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='IP Address',
        required=True,
        inputs={'configuration': 'configuration', 'address': 'ip_address'},
        result_decorator=None,
        enable_on_complete=['mac_address', 'url', 'file', 'boolean_checked', 'boolean_unchecked', 'date_time', 'submit']
    )

    mac_address = CustomStringField(
        label='MAC Address',
        default='11:11:11:11:11:11',
        validators=[MacAddress()]
    )

    url = StringField(
        label='URL',
        default='http://www.example.com',
        validators=[URL()]
    )

    file = FileField(
        label='File'
    )

    boolean_checked = BooleanField(
        label='Use for true or false things',
        default='checked'
    )

    boolean_unchecked = BooleanField(
        label='default for field is unchecked'
    )

    date_time = DateTimeField(
        label='Date and Time:',
        default=datetime.datetime.now(),
        format='%Y-%m-%d %H:%M:%S'
    )

    submit = SubmitField(label='Submit')
