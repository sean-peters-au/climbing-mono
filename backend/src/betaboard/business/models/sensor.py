import dataclasses

@dataclasses.dataclass
class SensorModel:
    id: str = None
    name: str = ""
    ip_address: str = ""
    hold_id: str = ""
    last_ping: str = ""

    def asdict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ip_address': self.ip_address,
            'hold_id': self.hold_id,
            'last_ping': self.last_ping,
        }