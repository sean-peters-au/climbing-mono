# Board Photogrammetry

This was a quick proof-of-concept to prove that I could programmatically create a 
3D model of a climbing board with just images of it from different angles.

## Instructions

This almost certainly won't work without fiddling, but I did vaguely document what I did while getting
thist to work for myself (Mac M2)

1. `./setup.sh`
2. `pipenv install`
3. `pipenv run python build_model.py`
4. `cp example/mvs/scene_mesh_textured* board-model-viewer/public/models/`
