import dataclasses

@dataclasses.dataclass
class SensorModel:
    id: str = None
    name: str = ""
    ip_address: str = ""
    hold_id: str = ""
    last_ping: str = ""

    @classmethod
    def from_mongo(cls, mongo_sensor):
        return cls(
            id=str(mongo_sensor.id),
            name=mongo_sensor.name,
            ip_address=mongo_sensor.ip_address,
            hold_id=str(mongo_sensor.hold.id),
            last_ping=str(mongo_sensor.last_ping),
        )

    def asdict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ip_address': self.ip_address,
            'hold_id': self.hold_id,
            'last_ping': self.last_ping,
        }