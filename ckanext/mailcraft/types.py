from __future__ import annotations

from typing import IO, Tuple, Union

AttachmentWithType = Union[Tuple[str, IO[str], str], Tuple[str, IO[bytes], str]]
AttachmentWithoutType = Union[Tuple[str, IO[str]], Tuple[str, IO[bytes]]]
Attachment = Union[AttachmentWithType, AttachmentWithoutType]
