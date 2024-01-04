from __future__ import annotations

from typing import IO, Tuple, Union
from typing_extensions import NotRequired, TypedDict


AttachmentWithType = Union[Tuple[str, IO[str], str], Tuple[str, IO[bytes], str]]
AttachmentWithoutType = Union[Tuple[str, IO[str]], Tuple[str, IO[bytes]]]
Attachment = Union[AttachmentWithType, AttachmentWithoutType]


EmailData = TypedDict(
    "EmailData",
    {
        "Bcc": str,
        "Content-Type": NotRequired[str],
        "Date": str,
        "From": str,
        "MIME-Version": NotRequired[str],
        "Subject": str,
        "To": str,
        "X-Mailer": NotRequired[str],
        "redirected_from": NotRequired["list[str]"]
    },
)
