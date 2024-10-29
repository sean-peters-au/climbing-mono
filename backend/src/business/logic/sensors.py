import typing
import business.models.sensor
import db.dao.sensor_dao

def add_sensor(sensor_data):
    sensor_model = business.models.sensor.SensorModel(
        name=sensor_data['name'],
        ip_address=sensor_data['ip_address'],
        hold_id=sensor_data['hold_id'],
    )
    db.dao.sensor_dao.SensorDAO.save_sensor(sensor_model)

def get_sensor(sensor_id: str) -> business.models.sensor.SensorModel:
    return db.dao.sensor_dao.SensorDAO.get_sensor_by_id(sensor_id)

def get_sensors() -> typing.List[business.models.sensor.SensorModel]:
    return db.dao.sensor_dao.SensorDAO.get_all_sensors()
