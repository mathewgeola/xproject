from pprint import pformat

from tests.test_xsqlalchemy_model.item import PersonItem
from tests.test_xsqlalchemy_model.model import Person


class Spider:
    def run(self):
        item = PersonItem()
        item["name"] = "Tom"
        item["gender"] = "男"
        item["age"] = 24

        row = Person.get_row_by_data_id(item)
        if row:
            print("update:\n", pformat(row))
        else:
            print("insert:\n", pformat(item.to_dict()))

        Person.save(item)


if __name__ == '__main__':
    spider = Spider()
    spider.run()
