import typing
import db.schema
import business.models.sensor

class SensorDAO:
    @staticmethod
    def get_all_sensors() -> typing.List[business.models.sensor.SensorModel]:
        sensors = db.schema.Sensor.objects().all()
        return [business.models.sensor.SensorModel.from_mongo(sensor) for sensor in sensors]

    @staticmethod
    def get_sensor_by_id(sensor_id: str) -> business.models.sensor.SensorModel:
        sensor = db.schema.Sensor.objects(id=sensor_id).first()
        if not sensor:
            raise ValueError("Sensor with given ID does not exist.")
        return business.models.sensor.SensorModel.from_mongo(sensor)

    @staticmethod
    def save_sensor(sensor_model: business.models.sensor.SensorModel):
        # Fetch HoldSchema instance
        hold_schema = db.schema.Hold.objects(id=sensor_model.hold_id).first()
        if not hold_schema:
            raise ValueError("Hold with given ID does not exist.")
        sensor_schema = db.schema.Sensor(
            name=sensor_model.name,
            ip_address=sensor_model.ip_address,
            hold=hold_schema,
        )
        sensor_schema.save()
        sensor_model.id = str(sensor_schema.id)