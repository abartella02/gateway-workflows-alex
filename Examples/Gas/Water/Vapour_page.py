# Copyright 2020 BlueCat Networks (USA) Inc. and its affiliates. All Rights Reserved.
import os
import sys
import codecs

from flask import url_for, redirect, render_template, flash, g

from bluecat import route, util
import config.default_config as config
from main_app import app
from .Water_form import GenericFormTemplate


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/Water/Vapour_endpoint')
@util.workflow_permission_required('Vapour_page')
@util.exception_catcher
@util.ui_secure_endpoint
def Water_Vapour_page():
    form = GenericFormTemplate()
    # Remove this line if your workflow does not need to select a configuration
    form.configuration.choices = util.get_configurations(default_val=True)
    return render_template(
        'Vapour_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
    )


@route(app, '/Water/form', methods=['POST'])
@util.workflow_permission_required('Vapour_page')
@util.exception_catcher
@util.ui_secure_endpoint
def Water_Vapour_page_form():
    form = GenericFormTemplate()
    # Remove this line if your workflow does not need to select a configuration
    form.configuration.choices = util.get_configurations(default_val=True)
    if not form.validate_on_submit():
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'Vapour_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
        )

    print(form.configuration.data)
    print(form.email.data)
    print(form.password.data)
    print(form.mac_address.data)
    print(form.ip_address.data)
    print(form.url.data)
    print(form.file.data)
    print(form.boolean_checked.data)
    print(form.boolean_unchecked.data)
    print(form.date_time.data)
    print(form.submit.data)

    # Put form processing logic here
    g.user.logger.info('SUCCESS')
    flash('success', 'succeed')
    return redirect(url_for('WaterWater_Vapour_page'))
