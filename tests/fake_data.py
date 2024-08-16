import locale
from faker import Faker

faker = Faker()
faker_local = Faker(locale.getdefaultlocale()[0])


def fake_filename() -> str:
    return faker.file_name(extension='')


def fake_suffix(prefix: str = '.') -> str:
    return '.' + faker.file_extension()
