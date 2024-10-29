import numpy as np
import mongoengine
import datetime

import utils.encoding

class CompressedMaskField(mongoengine.StringField):
    def to_python(self, value):
        if value is not None:
            if isinstance(value, str):
                if not value or value == '0|':
                    # Handle empty mask
                    return []
                try:
                    width_str, encoded_data = value.split('|', 1)
                    width = int(width_str)
                    if not encoded_data:
                        return []
                    bit_string = utils.encoding.rle_decode(encoded_data, delimiter='|')
                    bool_list = [bit == '1' for bit in bit_string]
                    decoded_mask = [bool_list[i:i + width] for i in range(0, len(bool_list), width)]
                    return decoded_mask
                except ValueError as e:
                    # Log the error and return an empty list
                    print(f"Error decoding mask value '{value}': {e}")
                    return []
            elif isinstance(value, list):
                # Value is in the old format; return as is
                return value
            else:
                raise ValueError(f"Unexpected data type for mask field: {type(value)}")
        return value

    def to_mongo(self, value):
        if value is not None:
            if isinstance(value, str):
                # Already compressed; return as is
                return value
            elif isinstance(value, list):
                if not value or len(value) == 0:
                    # Store empty masks as '0|'
                    return '0|'
                # Compress the mask
                flat_list = [item for sublist in value for item in sublist]
                if not flat_list:
                    return '0|'
                bit_string = ''.join(['1' if x else '0' for x in flat_list])
                encoded_data = utils.encoding.rle_encode(bit_string, delimiter='|')
                encoded_mask = f"{len(value[0])}|{encoded_data}"
                return encoded_mask
            else:
                raise ValueError(f"Unexpected data type for mask field: {type(value)}")
        return value

    def validate(self, value):
        print('validate called')
        if not isinstance(value, (list, str)):
            self.error(f"Invalid type for mask field: {type(value)}")


class Climber(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    climbed_routes = mongoengine.ListField(mongoengine.ReferenceField('Route'))

class Wall(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    height = mongoengine.IntField()
    width = mongoengine.IntField()
    image = mongoengine.UUIDField(binary=False)
    holds = mongoengine.ListField(mongoengine.ReferenceField('Hold'))
    routes = mongoengine.ListField(mongoengine.ReferenceField('Route'))

class Hold(mongoengine.Document):
    bbox = mongoengine.ListField(mongoengine.IntField())
    mask = CompressedMaskField()

class Route(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    grade = mongoengine.IntField(required=True)
    holds = mongoengine.ListField(mongoengine.ReferenceField(Hold))
    created_by = mongoengine.ReferenceField(Climber)
    date = mongoengine.DateTimeField()
    description = mongoengine.StringField()
    wall_id = mongoengine.ReferenceField(Wall)

class Sensor(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    ip_address = mongoengine.StringField(required=True, unique=True)
    hold = mongoengine.ReferenceField('Hold', required=True)
    last_ping = mongoengine.DateTimeField(default=datetime.datetime.utcnow)

class SensorReading(mongoengine.EmbeddedDocument):
    hold = mongoengine.ReferenceField('Hold', required=True)
    x = mongoengine.FloatField(required=True)  # Force component in the X direction (N)
    y = mongoengine.FloatField(required=True)  # Force component in the Y direction (N)

class Recording(mongoengine.Document):
    route = mongoengine.ReferenceField('Route', required=True)
    climber = mongoengine.ReferenceField('Climber', required=False)  # If you have user authentication
    start_time = mongoengine.DateTimeField(required=True)
    end_time = mongoengine.DateTimeField()
    frequency = mongoengine.FloatField(required=False, default=100)  # Frequency of data collection in Hz
    sensor_readings = mongoengine.ListField(
        mongoengine.ListField(
            mongoengine.EmbeddedDocumentField(SensorReading)
        )
    )  # Stores force data from sensors