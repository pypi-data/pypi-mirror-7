"""Initialize the database with data for the Age model.

The database must be empty otherwise an Integrity error will be raised. The
table is not cleared first in case the script is run inadvertently on an
existing database.
"""
from checklists import get_data_path
from checklists.models import Age, set_current_user, clear_current_user
from checklists.utils import i18n_fieldnames

from utils import create_objects, get_data


def run():
    set_current_user('load_ages')
    fields = ('id', 'slug') + i18n_fieldnames('name')
    data = get_data(get_data_path('age.csv'))
    create_objects(Age, fields, data)
    clear_current_user()
