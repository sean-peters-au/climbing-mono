import numpy as np
import mongoengine
import datetime

import utils.encoding

class CompressedMaskField(mongoengine.StringField):
    def to_mongo(self, value):
        if value is not None:
            # Check if the value is a numpy.ndarray and convert it to a list of lists
            if isinstance(value, np.ndarray):
                value = value.tolist()

            # Encode the mask
            flat_list = [item for sublist in value for item in sublist]
            bit_string = ''.join(['1' if x else '0' for x in flat_list])
            encoded_data = utils.misc_helpers.rle_encode(bit_string)
            encoded_mask = str(len(value[0])) + '|' + encoded_data

            return encoded_mask
        return value

    def to_python(self, value):
        if value is not None:
            # Decode the mask
            width, encoded_data = value.split('|', 1)
            width = int(width)
            bit_string = utils.misc_helpers.rle_decode(encoded_data)
            bool_list = [bit == '1' for bit in bit_string]
            decoded_mask = [bool_list[i:i + width] for i in range(0, len(bool_list), width)]

            return decoded_mask
        return value

    def validate(self, value):
        super(CompressedMaskField, self).validate(value)

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
    mask = mongoengine.ListField(mongoengine.ListField(mongoengine.BooleanField()))

class Route(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    grade = mongoengine.IntField(required=True)
    wall_id = mongoengine.ReferenceField(Wall)
    holds = mongoengine.ListField(mongoengine.ReferenceField(Hold))
    created_by = mongoengine.ReferenceField(Climber)
    date = mongoengine.DateTimeField()
    description = mongoengine.StringField()

class Sensor(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    ip_address = mongoengine.StringField(required=True, unique=True)
    hold = mongoengine.ReferenceField('Hold', required=True)
    last_ping = mongoengine.DateTimeField(default=datetime.datetime.utcnow)

class Recording(mongoengine.Document):
    route = mongoengine.ReferenceField('Route', required=True)
    user = mongoengine.ReferenceField('Climber', required=False)  # If you have user authentication
    start_time = mongoengine.DateTimeField(required=True)
    end_time = mongoengine.DateTimeField()
    sensor_data = mongoengine.ListField(mongoengine.DictField())  # Stores force data from sensors