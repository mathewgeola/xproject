import xproject
from tests.test_xsqlalchemy_model.model import Person


class PersonItem(xproject.xspider.xitems.xitem.Item):
    _MODEL = Person
