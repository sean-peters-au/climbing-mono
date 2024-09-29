import dataclasses

@dataclasses.dataclass
class Sensor:
    id: str
    ip_address: str
    hold_id: str