from __future__ import annotations

from typing import TypedDict

from typing_extensions import NotRequired


class Attachment(TypedDict):
    """Attachment structure."""

    name: str
    content: bytes
    media_type: NotRequired[str | None]
    cid: NotRequired[str | None]
    disposition: NotRequired[str]


class AttachmentData(TypedDict):
    """Attachment data structure."""

    filename: str
    content_id: NotRequired[str | None]
    disposition: str
    content_type: str
    size: int
    data: NotRequired[bytes | None]


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
        "attachments": NotRequired["list[AttachmentData]"],
    },
)
