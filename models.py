from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class Coordinates:
    x: float
    y: float

@dataclass
class ParkingSector:
    id: Optional[str] = None
    count: Optional[int] = None
    start: Optional[Coordinates] = None
    start2: Optional[Coordinates] = None
    end: Optional[Coordinates] = None
    width: Optional[float] = None
    height: Optional[float] = None
    groups: List[ParkingSector] = field(default_factory=list)
    multiline: List[Coordinates] = field(default_factory=list)
    numbering: Optional[str] = None
    layout: Optional[str] = None
    parking_angle: Optional[float] = None
    side: Optional[bool] = None
    direction: Optional[bool] = None
    skip: Optional[int] = None
    length: Optional[float] = None
    # additional fields may be added dynamically (e.g., total_groups, current_group)


def _parse_coordinates(data: dict | None) -> Optional[Coordinates]:
    if not data:
        return None
    return Coordinates(x=data["x"], y=data["y"])


def parse_parking_sector(data: dict) -> ParkingSector:
    groups = [parse_parking_sector(g) for g in data.get("groups", [])]
    multiline = [_parse_coordinates(p) for p in data.get("multiline", [])]
    return ParkingSector(
        id=data.get("id"),
        count=data.get("count"),
        start=_parse_coordinates(data.get("start")),
        start2=_parse_coordinates(data.get("start2")),
        end=_parse_coordinates(data.get("end")),
        width=data.get("width"),
        height=data.get("height"),
        groups=groups,
        multiline=[p for p in multiline if p is not None],
        numbering=data.get("numbering"),
        layout=data.get("layout"),
        parking_angle=data.get("parking_angle"),
        side=data.get("side"),
        direction=data.get("direction"),
        skip=data.get("skip"),
        length=data.get("length"),
    )
