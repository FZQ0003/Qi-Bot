"""TODO: Virtual shell config model."""
from ..model import QiModel, field_validator


# TODO: Move to module?
class ShellConfigModel(QiModel):
    """Model for virtual shell config."""
    timeout: int | float = 30
    shell_exec: list[str] = ['bash']
    check_dir: str = 'tmp/shell'
    output_replace: dict[str, str] = {}

    # noinspection PyNestedDecorators
    @field_validator('timeout')
    @classmethod
    def __timeout(cls, data: int | float) -> int | float:
        return data if data > 5 else 5

    # noinspection PyNestedDecorators
    @field_validator('shell_exec', mode='before')
    @classmethod
    def __shell_exec(cls, data: list[str] | str) -> list[str]:
        if isinstance(data, str):
            return data.split(' ')
        return data
