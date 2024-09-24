import utils.misc_helpers
import numpy as np  # Added import for numpy
from flask import current_app
from mongoengine import Document, UUIDField, StringField, IntField, ListField, ReferenceField, DateTimeField, BooleanField

class CompressedMaskField(StringField):
    def to_mongo(self, value):
        print('to_mongo')
        if value is not None:
            # Check if the value is a numpy.ndarray and convert it to a list of lists
            if isinstance(value, np.ndarray):
                value = value.tolist()
            # Flatten the list of lists of booleans to a single list
            flat_list = [item for sublist in value for item in sublist]
            # Convert boolean list to a string of '1's and '0's
            bit_string = ''.join(['1' if x else '0' for x in flat_list])
            # Encode the bit string using runlength encoding
            encoded_data = utils.misc_helpers.rle_encode(bit_string)
            # Store the width of the mask and the encoded data
            return str(len(value[0])) + '|' + encoded_data
        return value

    def to_python(self, value):
        if value is not None:
            # Separate the width and the encoded data
            width, encoded_data = value.split('|', 1)
            width = int(width)
            # Decode the runlength encoded data
            bit_string = utils.misc_helpers.rle_decode(encoded_data)
            # Convert the string of '1's and '0's back to a list of lists of booleans
            bool_list = [bit == '1' for bit in bit_string]
            # Split the flat list back into the original list of lists
            return [bool_list[i:i + width] for i in range(0, len(bool_list), width)]
        return value

    def validate(self, value):
        # No need to override validate, StringField's validate is sufficient
        super(CompressedMaskField, self).validate(value)


class Climber(Document):
    name = StringField(required=True)
    climbed_routes = ListField(ReferenceField('Route'))
    owns_walls = ListField(ReferenceField('Wall'))

class Wall(Document):
    name = StringField(required=True)
    height = IntField()
    width = IntField()
    image = UUIDField(binary=False)
    holds = ListField(ReferenceField('Hold'))
    routes = ListField(ReferenceField('Route'))

class Hold(Document):
    bbox = ListField(IntField())
    mask = ListField(ListField(BooleanField()))

class Route(Document):
    name = StringField(required=True)
    grade = IntField(required=True)
    wall_id = ReferenceField(Wall)
    holds = ListField(ReferenceField(Hold))
    created_by = ReferenceField(Climber)
    date = DateTimeField()
    description = StringField()