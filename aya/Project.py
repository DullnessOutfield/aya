from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
from functools import cached_property
from typing import Optional, List, Dict, Tuple, Any
from .KismetDevice import KismetDevice
from .lib import get_devs


@dataclass
class Survey:
    path: Path
    name: str
    location: Tuple[float, float] = field(default_factory=tuple)
    devices: List[KismetDevice] = field(default_factory=list)

    def __post_init__(self):
        if not self.name:
            self.name = self.path.stem


    def get_devices(self) -> List[KismetDevice]:
        return get_devs(self.path)

    @cached_property
    def access_points(self) -> List[KismetDevice]:
        return [
            device
            for device in self.devices
            if device.device_type in ("Wi-Fi AP", "Wi-Fi Bridged")
        ]

@dataclass
class Project:
    name: str
    surveys: List[Survey] = field(default_factory=list)

    @property
    def all_devices(self) -> List[KismetDevice]:
        """Get all devices across all surveys"""
        devices = []
        for survey in self.surveys:
            devices.extend(survey.devices)
        return devices
