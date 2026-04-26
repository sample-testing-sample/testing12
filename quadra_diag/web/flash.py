from typing import TypedDict

from fastapi import Request


class FlashMessage(TypedDict):
    level: str
    message: str


def push_flash(request: Request, message: str, level: str = "info") -> None:
    queue = request.session.setdefault("_flashes", [])
    queue.append({"level": level, "message": message})
    request.session["_flashes"] = queue


def pop_flashes(request: Request) -> list[FlashMessage]:
    flashes = request.session.pop("_flashes", [])
    return flashes
