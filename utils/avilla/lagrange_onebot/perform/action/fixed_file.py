from __future__ import annotations

import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import IO, TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.file import (
    FileCapability
)

if TYPE_CHECKING:
    from avilla.onebot.v11.account import OneBot11Account  # noqa
    from avilla.onebot.v11.protocol import OneBot11Protocol  # noqa


class OneBot11FixedFileActionPerform((m := AccountCollector["OneBot11Protocol", "OneBot11Account"]())._):
    m.namespace = "avilla.protocol/onebot11-fixed::action"
    m.identify = "file"

    @m.entity(FileCapability.upload, target="land.friend")
    async def upload_private_file(
        self,
        target: Selector,
        name: str,
        file: bytes | IO[bytes] | os.PathLike,
        path: str | None = None,
    ) -> None:
        _name = name or ""
        _path = path or ""
        if "/" in _path and not _name:
            _path, _name = _path.rsplit("/", 1)

        if isinstance(file, os.PathLike):
            await self.account.connection.call(
                "upload_private_file",
                {
                    "user_id": int(target["friend"]),
                    "file": Path(file).resolve().as_posix(),
                    "name": _name,
                },
            )
        else:
            with NamedTemporaryFile() as temp:
                temp.write(file)  # type: ignore
                temp.flush()
                await self.account.connection.call(
                    "upload_private_file",
                    {
                        "user_id": int(target["friend"]),
                        "file": temp.name,
                        "name": _name,
                    },
                )
