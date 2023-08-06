# -*- coding:utf-8 -*-
try:
    import django
except ImportError:
    LIB_ENABLED_DJANGO = False
else:
    LIB_ENABLED_DJANGO = True


def lower_class_name(obj):
    return obj.__class__.__name__.lower()


def get_django_version():
    return django.VERSION


def initialize():
    from django.conf import settings
    settings_dict = dict(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            },
        },
    )
    settings.configure(**settings_dict)


def get_connection():
    "get default database connection"
    from django.db import connections
    connection = connections['default']
    return connection


def get_cursor(connection):
    "get database cursor from connection"
    return connection.cursor()


def get_style():
    from django.core.management.color import no_style
    return no_style()


def create_table(model):
    connection = get_connection()
    cursor = get_cursor(connection)
    style = get_style()

    sql, references = connection.creation.sql_create_model(
        model, style)
    for statement in sql:
        cursor.execute(statement)

    for f in model._meta.many_to_many:
        create_table(f.rel.through)


def _setup_db():
    return get_connection()


def _teardown_db():
    get_connection().close()
