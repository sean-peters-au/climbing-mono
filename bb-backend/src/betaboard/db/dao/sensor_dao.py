import typing
import sqlalchemy.orm

import betaboard.db.schema.sensor_schema as sensor_schema
import betaboard.business.models.sensor as sensor_model
import betaboard.db.dao.base_dao as base_dao

class SensorDAO:
    @staticmethod
    def _to_model(sensor: sensor_schema.SensorSchema) -> sensor_model.SensorModel:
        return sensor_model.SensorModel(
            id=str(sensor.id),
            name=sensor.name,
            ip_address=sensor.ip_address,
            hold_id=str(sensor.hold_id),
        )

    @staticmethod
    @base_dao.with_session
    def get_all_sensors(
        session: sqlalchemy.orm.Session
    ) -> typing.List[sensor_model.SensorModel]:
        sensors = session.query(sensor_schema.SensorSchema).all()
        return [SensorDAO._to_model(sensor) for sensor in sensors]

    @staticmethod
    @base_dao.with_session
    def get_sensor_by_id(
        sensor_id: int,
        session: sqlalchemy.orm.Session
    ) -> sensor_model.SensorModel:
        sensor = session.query(sensor_schema.SensorSchema).get(sensor_id)
        if sensor is None:
            raise ValueError("Sensor with given ID does not exist.")
        return SensorDAO._to_model(sensor)

    @staticmethod
    @base_dao.with_session
    def save_sensor(
        sensor_model: sensor_model.SensorModel,
        session: sqlalchemy.orm.Session
    ):
        # Verify hold exists
        hold = session.query(sensor_schema.HoldSchema).get(sensor_model.hold_id)
        if hold is None:
            raise ValueError("Hold with given ID does not exist.")

        sensor = sensor_schema.SensorSchema(
            name=sensor_model.name,
            ip_address=sensor_model.ip_address,
            hold_id=sensor_model.hold_id,
        )
        session.add(sensor)
        session.flush()
        sensor_model.id = str(sensor.id)