# Copyright (c) 2009 Guilherme Gondim and contributors
#
# This file is part of Django Smuggler.
#
# Django Smuggler is free software under terms of the GNU Lesser
# General Public License version 3 (LGPLv3) as published by the Free
# Software Foundation. See the file README for copying conditions.

import os
from django.core import serializers
from django.core.management import CommandError
from django.core.management.color import no_style
from django.core.management.commands.dumpdata import Command as DumpData
from django.db import connections, transaction, router
from django.db.utils import DEFAULT_DB_ALIAS
from django.http import HttpResponse
from django.utils.six import StringIO
from smuggler.settings import (SMUGGLER_FORMAT, SMUGGLER_INDENT)

try:
    allow_migrate = router.allow_migrate
except AttributeError:  # before django 1.7
    allow_migrate = router.allow_syncdb


def get_file_list(path):
    file_list = []
    for file_name in os.listdir(path):
        if not os.path.isdir(file_name):
            file_path = os.path.join(path, file_name)
            file_size = os.path.getsize(file_path)
            file_list.append((file_name, '%0.1f KB' % float(file_size/1024.0)))
    file_list.sort()
    return file_list


def save_uploaded_file_on_disk(uploaded_file, destination_path):
    with open(destination_path, 'wb') as fp:
        for chunk in uploaded_file.chunks():
            fp.write(chunk)


def serialize_to_response(app_labels=[], exclude=[], response=None,
                          format=SMUGGLER_FORMAT, indent=SMUGGLER_INDENT):
    response = response or HttpResponse(content_type='text/plain')
    stream = StringIO()
    error_stream = StringIO()
    try:
        dumpdata = DumpData()
        dumpdata.style = no_style()
        dumpdata.execute(*app_labels, **{
            'exclude': exclude,
            'format': format,
            'indent': indent,
            'show_traceback': True,
            'use_natural_keys': True,
            'stdout': stream,
            'stderr': error_stream
        })
    except SystemExit:
        # Django 1.4's implementation of execute catches CommandErrors and
        # then calls sys.exit(1), we circumvent this here.
        errors = error_stream.getvalue().strip().replace('Error: ', '')
        raise CommandError(errors)
    response.write(stream.getvalue())
    return response


def load_requested_data(data):
    """
    Load the given data dumps and return the number of imported objects.

    Wraps the entire action in a big transaction.

    """
    style = no_style()

    using = DEFAULT_DB_ALIAS
    connection = connections[using]
    cursor = connection.cursor()
    models = set()
    counter = 0
    # Django < 1.6 has no atomic transaction manager, use commit_on_success
    atomic = getattr(transaction, 'atomic',
                     getattr(transaction, 'commit_on_success'))

    with atomic(using=using):
        for format, stream in data:
            objects = serializers.deserialize(format, stream)
            for obj in objects:
                model = obj.object.__class__
                if allow_migrate(using, model):
                    models.add(model)
                    counter += 1
                    obj.save(using=using)
        if counter > 0:
            sequence_sql = connection.ops.sequence_reset_sql(style, models)
            if sequence_sql:
                for line in sequence_sql:
                    cursor.execute(line)
    return counter
