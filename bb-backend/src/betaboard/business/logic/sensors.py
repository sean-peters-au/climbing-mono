import typing

import betaboard.business.models.sensor as sensor_model
import betaboard.db.dao.sensor_dao as sensor_dao

def add_sensor(sensor_data):
    sensor_model = sensor_model.SensorModel(
        name=sensor_data['name'],
        ip_address=sensor_data['ip_address'],
        hold_id=sensor_data['hold_id'],
    )
    sensor_dao.SensorDAO.save_sensor(sensor_model)

def get_sensor(sensor_id: str) -> sensor_model.SensorModel:
    return sensor_dao.SensorDAO.get_sensor_by_id(sensor_id)

def get_sensors() -> typing.List[sensor_model.SensorModel]:
    return sensor_dao.SensorDAO.get_all_sensors()
