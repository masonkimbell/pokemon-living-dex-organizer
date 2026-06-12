from typing import TypedDict


class EntryRow(TypedDict):
    name: str
    number: str
    region: str
    form: int
    have: bool
    image_path: str
