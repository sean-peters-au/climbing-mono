import abc
import requests
import json

from betaboard.services import service

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class SensorService(service.Service):
    @abc.abstractmethod
    def get_sensor_force(self, sensor, start_time, end_time):
        pass

class VectorSensorService(SensorService):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.extensions['sensors'] = self

    def get_sensor_force(self, sensor, start_time, end_time):
        try:
            sensor_response = requests.get(
                f'http://{sensor.ip_address}/get_force_data',
                params={
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat()
                },
                timeout=5
            )
            sensor_response.raise_for_status()
            sensor_force_data = sensor_response.json()
            return ({
                'hold_id': str(sensor.hold.id),
                'force_data': sensor_force_data.get('forces', [])
            })
        except requests.RequestException as e:
            print(f"Error retrieving data from sensor {sensor.ip_address}: {e}")

class SimulatedSensorService(SensorService):
    def get_sensor_force(self, sensor, recording):
        with open(f'static/hold-vector-data/{sensor.hold.id}.json', 'r') as f:
            force_data = json.load(f)

        return ({
            'hold_id': str(sensor.hold.id),
            'force_data': force_data
        })