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
