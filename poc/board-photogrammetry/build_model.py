import os
import subprocess
from typing import Optional
import open3d as o3d

# Assuming OpenMVG is built in the parent directory
OPENMVG_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "openMVG"))
OPENMVG_BUILD = os.path.abspath(os.path.join(os.path.dirname(__file__), "openMVG", "build"))
OPENMVG_CAMERA_DB = os.path.abspath(os.path.join(os.path.dirname(__file__), "openMVG", "src", "openMVG", "exif", "sensor_width_database", "sensor_width_camera_database.txt"))
OPENMVS_BIN = "/usr/local/bin/OpenMVS"

def create_directories(project_dir: str):
    """
    Create necessary directories for the pipeline.
    """
    dirs = {
        'input': os.path.join(project_dir, 'images'),
        'matches': os.path.join(project_dir, 'matches'),
        'reconstruction': os.path.join(project_dir, 'reconstruction'),
        'mvs': os.path.join(project_dir, 'mvs'),
    }
    for dir_path in dirs.values():
        os.makedirs(dir_path, exist_ok=True)
    return dirs

def run_command(command, cwd=None):
    """Run a command and handle errors."""
    # Handle binary paths based on command type
    if command[0].startswith('openMVG'):
        command[0] = os.path.join(OPENMVG_BUILD, "Darwin-arm64-Release", command[0])
    elif command[0] in ['DensifyPointCloud', 'ReconstructMesh', 'RefineMesh', 'TextureMesh']:
        command[0] = os.path.join(OPENMVS_BIN, command[0])
    
    print(f"\nExecuting command in directory: {cwd or os.getcwd()}")
    print(f"Full command: {' '.join(command)}")
    
    result = subprocess.run(
        command, 
        cwd=cwd,
        capture_output=True,
        text=True,
        env=os.environ.copy()  # Explicitly pass environment variables
    )
    
    if result.returncode != 0:
        print("\nCommand failed with output:")
        print("\nSTDOUT:")
        print(result.stdout)
        print("\nSTDERR:")
        print(result.stderr)
        raise RuntimeError(f"Command {command[0].split('/')[-1]} failed with exit code {result.returncode}")
    
    return result

def check_log(mvs_dir: str, command_name: str) -> None:
    """Check the most recent log file for a command."""
    log_files = [f for f in os.listdir(mvs_dir) if f.startswith(command_name) and f.endswith('.log')]
    if log_files:
        latest_log = max(log_files)
        print(f"\nContents of {latest_log}:")
        with open(os.path.join(mvs_dir, latest_log), 'r') as f:
            print(f.read())

def check_ply_colors(file_path: str) -> None:
    """Check if a PLY file contains vertex colors."""
    if not os.path.exists(file_path):
        print(f"File does not exist: {file_path}")
        return
        
    mesh = o3d.io.read_triangle_mesh(file_path)
    print(f"\nChecking colors in {os.path.basename(file_path)}:")
    print(f"Has vertex colors: {mesh.has_vertex_colors()}")
    print(f"Vertices: {len(mesh.vertices)}")
    print(f"Triangles: {len(mesh.triangles)}")

def reconstruct(project_dir: str):
    """
    Reconstruct 3D model using OpenMVG and OpenMVS.
    """
    # Get absolute paths
    project_dir = os.path.abspath(project_dir)
    dirs = create_directories(project_dir)

    input_dir = dirs['input']
    matches_dir = dirs['matches']
    recon_dir = dirs['reconstruction']
    mvs_dir = dirs['mvs']
    
    # Create undistorted images directory
    undistorted_dir = os.path.join(mvs_dir, 'undistorted_images')
    os.makedirs(undistorted_dir, exist_ok=True)

    # 1. OpenMVG: Intrinsics analysis
    run_command([
        'openMVG_main_SfMInit_ImageListing',
        '-i', input_dir,
        '-o', matches_dir,
        '-d', OPENMVG_CAMERA_DB,
        '-f', '1723.0',  # Approximate focal length in pixels
    ])

    # 2. OpenMVG: Compute features
    run_command([
        'openMVG_main_ComputeFeatures',
        '-i', os.path.join(matches_dir, 'sfm_data.json'),
        '-o', matches_dir,
        '-f', '1',  # Force recomputation
        '-m', 'SIFT',  # Use SIFT descriptor
        '-p', 'NORMAL',  # Normal preset
    ])

    # 3. OpenMVG: Compute matches
    run_command([
        'openMVG_main_ComputeMatches',
        '-i', os.path.join(matches_dir, 'sfm_data.json'),
        '-o', os.path.join(matches_dir, 'matches.putative.bin'),  # Changed output name
        '-f', '1',  # Force recomputation
        '-r', '0.8',  # Ratio test
        '-n', 'FASTCASCADEHASHINGL2'  # Explicit matching method
    ])

    # 4. OpenMVG: Filter matches
    run_command([
        'openMVG_main_GeometricFilter',
        '-i', os.path.join(matches_dir, 'sfm_data.json'),
        '-m', os.path.join(matches_dir, 'matches.putative.bin'),
        '-g', 'f',  # Fundamental matrix filtering
        '-o', os.path.join(matches_dir, 'matches.f.bin'),
    ])

    # 5. OpenMVG: SfM reconstruction
    run_command([
        'openMVG_main_SfM',
        '-i', os.path.join(matches_dir, 'sfm_data.json'),
        '-m', matches_dir,
        '-M', os.path.join(matches_dir, 'matches.f.bin'),  # Specify matches file
        '-o', recon_dir,
    ])

    # 6. OpenMVG: Compute structure from known poses (optional)
    run_command([
        'openMVG_main_ComputeStructureFromKnownPoses',
        '-i', os.path.join(recon_dir, 'sfm_data.bin'),
        '-m', matches_dir,
        '-f', os.path.join(matches_dir, 'matches.f.bin'),
        '-o', os.path.join(recon_dir, 'structure.bin'),
    ])

    # 7. OpenMVG: Export to OpenMVS format
    run_command([
        'openMVG_main_openMVG2openMVS',
        '-i', os.path.join(recon_dir, 'sfm_data.bin'),
        '-o', os.path.join(mvs_dir, 'scene.mvs'),
        '-d', undistorted_dir,  # Specify where to save undistorted images
    ])

    # 8. OpenMVS: Densify point cloud
    scene_file = os.path.join(mvs_dir, 'scene.mvs')
    
    # Verify files exist
    print(f"\nChecking files before DensifyPointCloud:")
    print(f"Scene file exists: {os.path.exists(scene_file)}")
    
    run_command([
        'DensifyPointCloud',
        scene_file,
        '--verbosity', '2',  # Add verbosity for better logging
        '--resolution-level', '1',
        '--min-resolution', '640',
        '--max-resolution', '2048',
        '--number-views', '4',
        '--max-threads', '4',
        '-o', os.path.join(mvs_dir, 'scene_dense.mvs'),
    ], cwd=mvs_dir)  # Set the working directory directly

    # After dense point cloud generation
    dense_ply = os.path.join(mvs_dir, 'scene_dense.ply')
    print("\nAfter DensifyPointCloud:")
    check_ply_colors(dense_ply)

    # 9. OpenMVS: Reconstruct mesh
    dense_scene = os.path.join(mvs_dir, 'scene_dense.mvs')
    mesh_ply = os.path.join(mvs_dir, 'scene_mesh.ply')
    run_command([
        'ReconstructMesh',
        dense_scene,  # The MVS file for camera info
        '--pointcloud-file', dense_ply,  # The actual point cloud with colors
        '--verbosity', '2',
        '--remove-spurious', '0',
        '--smooth', '2',
        '--max-threads', '4',
        '--export-type', 'ply',
        '-o', mesh_ply,
    ], cwd=mvs_dir)
    check_log(mvs_dir, 'ReconstructMesh')

    # After mesh reconstruction
    print("\nAfter ReconstructMesh:")
    check_ply_colors(mesh_ply)

    # 10. OpenMVS: Refine mesh
    print(f"\nChecking files before RefineMesh:")
    print(f"Mesh file exists: {os.path.exists(mesh_ply)}")
    
    refined_ply = os.path.join(mvs_dir, 'scene_mesh_refined.ply')
    run_command([
        'RefineMesh',
        dense_scene,  # Use the original MVS file for camera info
        '--resolution-level', '1',
        '--max-threads', '4',
        '--mesh-file', mesh_ply,  # Input mesh
        '-o', refined_ply,  # Output mesh
    ], cwd=mvs_dir)
    check_log(mvs_dir, 'RefineMesh')

    # After mesh refinement
    print("\nAfter RefineMesh:")
    check_ply_colors(refined_ply)

    # 11. OpenMVS: Texture mesh
    textured_obj = os.path.join(mvs_dir, 'scene_mesh_textured')  # Remove extension
    run_command([
        'TextureMesh',
        dense_scene,  # Use the original MVS file for camera info
        '--mesh-file', refined_ply,
        '--export-type', 'obj',  # Explicitly set output format
        '--decimate', '0.5',     # Optionally reduce texture complexity
        '--verbosity', '2',
        '--texture-size', '8192',
        '--empty-color', '0',    # Fill empty areas with black
        '--close-holes', '30',
        '--resolution-level', '1',
        '-o', textured_obj,      # Output without extension
    ], cwd=mvs_dir)

    print("\nChecking generated files:")
    expected_files = [
        'scene_mesh_textured.obj',
        'scene_mesh_textured.mtl',
        'scene_mesh_textured_material_0.png'
    ]
    for file in expected_files:
        path = os.path.join(mvs_dir, file)
        print(f"{file}: {os.path.exists(path)}")

    textured_ply = os.path.join(mvs_dir, 'scene_mesh_textured.ply')
    check_ply_colors(textured_ply)

    print("3D reconstruction completed successfully.")

if __name__ == '__main__':
    
    project_directory = 'example'
    reconstruct(project_directory)