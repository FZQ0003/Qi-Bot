import secrets

from utils.file import CommonFile, JsonData
from utils.model import QiModel


class SampleModel(QiModel):
    a_int: int = secrets.randbits(32)
    b_str: str = secrets.token_hex()
    c_list_int: list[int] = [secrets.randbits(32) for _ in range(4)]


class SampleNestedModel(QiModel):
    x_str: str = 'Sample Nested Model for Test'
    y_model: SampleModel = SampleModel()


class SampleTempFile(CommonFile):
    prefix: str = 'tmp'
    category: str = 'test'


class SampleTempJson(JsonData):
    prefix: str = 'tmp'
    category: str = 'test'


class TestFile:

    def test_path(self):
        file = SampleTempFile(
            filename='foo.bar',
            suffix='.sample'
        )
        # tmp/test/foo.bar.sample
        path_str = f'{file.prefix}/{file.category}/{file.filename}{file.suffix}'
        file_2 = SampleTempFile.from_path(path_str)
        assert file.path.as_posix() == path_str
        assert file_2.path.as_posix() == path_str

    def test_io(self):
        data = secrets.token_bytes()
        file = SampleTempFile(
            filename='io',
            suffix='.bin',
            is_bin=True
        )
        file.write(data)
        assert file.exists is True
        assert isinstance((test_data := file.read()), bytes)
        assert test_data == data
        file.delete()
        assert file.exists is False

    def test_config(self):
        model = SampleNestedModel()
        file = SampleTempJson(filename='config')
        file.write(model)
        test_dict = file.read()
        test_model = file.read(SampleNestedModel)
        assert model.model_dump() == test_dict
        assert model.model_dump() == test_model.model_dump()
