import business.models.sensor
import db.schema

def add_sensor(sensor):
    db.schema.Sensor(**sensor).save()

def get_sensor(id):
    return business.models.sensor.Sensor.from_mongo(db.schema.Sensor.objects.get(id=id))

def get_sensors():
    return [business.models.sensor.Sensor.from_mongo(sensor) for sensor in db.schema.Sensor.objects]