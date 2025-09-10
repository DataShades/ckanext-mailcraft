from __future__ import annotations

from typing import IO

from typing_extensions import NotRequired, TypedDict

AttachmentWithType = tuple[str, IO[str], str] | tuple[str, IO[bytes], str]
AttachmentWithoutType = tuple[str, IO[str]] | tuple[str, IO[bytes]]
Attachment = AttachmentWithType | AttachmentWithoutType


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
        "redirected_from": NotRequired["list[str]"],
    },
)
