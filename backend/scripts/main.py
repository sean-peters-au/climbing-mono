from flask import Flask, request
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator

import cv2
import numpy as np

# Define the image file and model details
IMAGE_FILE_NAME = './medium-wall-stokt-1.png'
MODEL_TYPE = "vit_h"  # Chosen from available model types: vit_h, vit_l, vit_b
CHECKPOINT_PATH = 'sam_vit_h_4b8939.pth'
SEGMENT_WHAT = 'climbing holds'

# Initialize the model
sam = sam_model_registry[MODEL_TYPE](checkpoint=CHECKPOINT_PATH)
mask_generator = SamAutomaticMaskGenerator(sam)

app = Flask(__name__)

@app.route('/upload_wall_image', methods=['POST'])
def upload_wall_image():
    if 'image' not in request.files:
        return "No image provided", 400
    
    file = request.files['image']
    if file.filename == '':
        return "No selected file", 400

        


if __name__ == '__main__':
    app.run(debug=True)


from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import BYTEA

Base = declarative_base()

class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    image_data = Column(BYTEA, nullable=False)  # Storing image as binary data
    masks = relationship('Mask', back_populates='image')  # One-to-many relationship with masks

class Mask(Base):
    __tablename__ = 'masks'
    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, ForeignKey('images.id'), nullable=False)
    mask_data = Column(BYTEA, nullable=False)  # Storing mask as binary data
    area = Column(Integer)
    bbox = Column(String)  # Storing bbox as a string, e.g., "x1,y1,x2,y2"
    predicted_iou = Column(Float)
    stability_score = Column(Float)
    image = relationship('Image', back_populates='masks')  # Many-to-one relationship with image
    centroids = relationship('Centroid', back_populates='mask')  # One-to-many relationship with centroids

class Centroid(Base):
    __tablename__ = 'centroids'
    id = Column(Integer, primary_key=True)
    mask_id = Column(Integer, ForeignKey('masks.id'), nullable=False)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    mask = relationship('Mask', back_populates='centroids')  # Many-to-one relationship with mask

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('postgresql://user:password@localhost/dbname')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a session
session = Session()