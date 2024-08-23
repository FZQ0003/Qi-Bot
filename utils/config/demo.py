"""Development config models."""
from typing import Iterator

from ..model import QiModel, model_validator


class DemoConfigModel(QiModel):
    """Model for demo config."""
    pattern: dict[str, list[dict[str, str]]] = {}

    # noinspection PyNestedDecorators
    @model_validator(mode='before')
    @classmethod
    def __parse_args(cls, data: dict[str, ...]) -> dict[str, ...]:
        if isinstance(data, dict):
            data_new = {}
            for land, selectors in data.items():
                if isinstance(selectors, list):
                    selectors_new = []
                    for selector in selectors:
                        if isinstance(selector, dict):
                            selector = [selector]
                        selector = {str(k): str(v) for d in selector for k, v in d.items()}
                        selectors_new.append(selector)
                    data_new[land] = selectors_new
            return {'pattern': data_new}
        return data

    def get_selectors(self, *lands: str) -> Iterator[dict[str, str]]:
        if len(lands) < 1:
            lands = self.pattern.keys()
        for land in set(lands):
            selectors = self.pattern.get(land, [])
            for selector in selectors:
                yield {'land': land, **selector}
