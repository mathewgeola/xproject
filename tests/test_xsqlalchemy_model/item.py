import xproject
from tests.test_xsqlalchemy_model.model import PersonModel


class PersonItem(xproject.Item):
    MODEL = PersonModel
