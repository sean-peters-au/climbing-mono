import os
import sys
import open3d as o3d
from typing import Optional


def view_model(model_path: str, window_name: Optional[str] = "3D Model Viewer") -> None:
    """
    View a 3D model using Open3D.
    
    Args:
        model_path: Path to the model file (.ply, .obj, etc.)
        window_name: Name of the viewer window
    """
    # Check if file exists
    if not os.path.exists(model_path):
        print(f"Error: File {model_path} does not exist")
        sys.exit(1)

    # Load the geometry based on file extension
    file_extension = os.path.splitext(model_path)[1].lower()
    
    if file_extension == '.ply':
        mesh = o3d.io.read_triangle_mesh(model_path)
        # Compute normals for better visualization
        mesh.compute_vertex_normals()
    elif file_extension == '.obj':
        mesh = o3d.io.read_triangle_mesh(model_path)
        # Compute normals for better visualization
        mesh.compute_vertex_normals()
    else:
        print(f"Error: Unsupported file format {file_extension}")
        sys.exit(1)

    # Create visualizer
    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name=window_name)
    
    # Add the geometry
    vis.add_geometry(mesh)
    
    # Set default camera view
    ctr = vis.get_view_control()
    ctr.set_zoom(0.8)
    
    # Run the visualizer
    vis.run()
    vis.destroy_window()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python view_model.py <path_to_model>")
        sys.exit(1)
    
    model_path = sys.argv[1]
    view_model(model_path)