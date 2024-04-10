"""Base file (common file, config, data) manager."""
from functools import wraps, cached_property
from pathlib import Path
from typing import Callable, TypeVar, ParamSpec

from .error import DataCheckError
from ..model import QiModel, field_validator, ConfigDict
from ..model.types import Filename, Filemode

T = TypeVar('T')
P = ParamSpec('P')
Model = TypeVar('Model')

__all__ = [
    'CommonFile',
    'DataFile',
    'Data',
    'ConfigFile',
    'Config'
]


class CommonFile(QiModel):
    """Common file manager.

    Attributes:
        filename (str): File name.
        prefix (str): File prefix.
        category (str): File category. (e.g. "image")
        suffix (str): File suffix. (e.g. ".png")
        is_bin (bool): Whether the file is binary file.
        mode (int): File mode (maybe useful for security).

    Notes:
        Output path: "prefix/category/filename.suffix" (relative).

        The class is NOT editable.
    """
    filename: Filename
    prefix: str = ''
    category: str = ''
    suffix: str = ''
    is_bin: bool = True
    mode: Filemode = 0o644

    # Readonly
    model_config = ConfigDict(frozen=True)

    # noinspection PyNestedDecorators
    @field_validator('suffix')
    @classmethod
    def __parse_suffix(cls, data: str) -> str:
        if data.startswith('.') or not data:
            return data
        return '.' + data

    @classmethod
    def from_path(cls, path: Path | str, **kwargs) -> 'CommonFile':
        """Init from a path-like string.

        Notes:
            Some attributes (prefix, category, filename and suffix) will be redefined.
        """
        if isinstance(path, str):
            path = Path(path)
        return cls(
            filename=path.stem,
            prefix=path.parent.as_posix(),
            category='',
            suffix=path.suffix,
            **kwargs
        )

    def __str__(self) -> str:
        return self.path.as_posix()

    @cached_property
    def path(self) -> Path:
        """Return a Path class of the file."""
        return Path(self.prefix, self.category, f'{self.filename}{self.suffix}')

    @property
    def exists(self) -> bool:
        """Check whether the file exists."""
        return self.path.is_file()

    def read(self) -> bytes | str:
        """Open the file and return an object based on filetype."""
        # Raise errors by Path object
        if self.is_bin:
            return self.path.read_bytes()
        else:
            # Do not check newline at EOF
            return self.path.read_text()

    def write(self, data: bytes | str) -> int:
        """White bytes or string to the file."""
        if not self.path.parent.is_dir():
            self.path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        self.path.touch(mode=self.mode, exist_ok=True)
        if self.is_bin:
            return self.path.write_bytes(data)
        else:
            # Do not check newline at EOF
            return self.path.write_text(data)

    def delete(self):
        """Delete the file."""
        self.path.unlink(True)


class DataFile(CommonFile):
    """Data file manager.

    Notes:
        Use @executor() to manage automatically::

            datafile = DataFile(filename='datafile', suffix='.txt', is_bin=False)
            @datafile.executor(read=True, write=False)
            def generate_data(param: ...) -> ...:
                ...
    """

    def _exec_pre(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """Pre-processing function for initializing, parsing inputs, etc."""
        ...

    # noinspection PyMethodMayBeStatic, PyUnusedLocal
    def _exec_post(self, _data: T, *args: P.args, **kwargs: P.kwargs) -> bytes | str:
        """Post-processing function for parsing NEWLY GENERATED data."""
        # Check whether the data is empty
        if not _data:
            raise DataCheckError(f'No output!')
        return _data

    def executor(self, read: bool = True, write: bool = True) \
            -> Callable[[Callable[P, T]], Callable[P, T]]:
        """Decorator for fetching data.

        If "read" flag enabled and the file exists, read and return data;
        otherwise execute the decorated function, write to file
        (if "write" flag enabled) and return output.

        Notes:
            You may implement _exec_pre() and _exec_post() when extending the class.

            Known issue: Type checking may not be passed. Use #noqa to avoid this.
        """

        def __func(func: Callable[P, T]) -> Callable[P, T]:
            @wraps(func)
            def __wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                # Pre-processing function
                self._exec_pre(*args, **kwargs)
                # Read data (and return)
                if read:
                    try:
                        return self.read()
                    except OSError:
                        pass
                # Decorated function
                output = func(*args, **kwargs)
                # Post-processing function
                output = self._exec_post(output, args, kwargs)
                # Write data and return
                if write:
                    try:
                        self.write(output)
                    except OSError:
                        pass
                return output

            return __wrapper

        return __func


class Data(DataFile):
    """Data with prefix."""
    prefix: str = 'data'


class ConfigFile(CommonFile):
    """Config file manager (str <-> dict <-> class).
    Use reader() and writer() to handle different types.
    """
    is_bin: bool = False

    # @staticmethod
    # def load(io: IOBase) -> dict:
    #     raise NotImplementedError
    #
    # @staticmethod
    # def dump(data: dict) -> IOBase:
    #     raise NotImplementedError

    @staticmethod
    def loads(string: str) -> dict:
        """Load config from string."""
        raise NotImplementedError

    @staticmethod
    def dumps(data: dict) -> str:
        """Dump config to string."""
        raise NotImplementedError

    def read(self, target_model: type[Model] = dict) -> Model:
        output = self.loads(super().read())
        if target_model is dict:
            return output
        return target_model(**output)

    def write(self, data: Model) -> int:
        if not isinstance(data, dict):
            try:
                data = data.model_dump()
            except AttributeError:
                # Warning: It cannot dump complex models!
                data = dict(data)
        return super().write(self.dumps(data))


# noinspection PyAbstractClass
class Config(ConfigFile):
    """Config with prefix."""
    prefix: str = 'config'
