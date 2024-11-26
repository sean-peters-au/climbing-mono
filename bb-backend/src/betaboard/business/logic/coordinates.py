import dataclasses
import typing

import numpy as np
import cv2


@dataclasses.dataclass
class WallFace:
    """Represents a planar section of the climbing wall.
    
    Args:
        normal: Unit normal vector to the face
        origin: Point where face meets the ground in global coordinates
        rotation: 3x3 rotation matrix from global to face coordinates
    """
    normal: np.ndarray  # 3D unit vector
    origin: np.ndarray  # 3D point
    rotation: np.ndarray  # 3x3 matrix


@dataclasses.dataclass
class CalibrationData:
    """Stores parameters needed for coordinate transformations.
    
    Args:
        camera_matrix: 3x3 camera intrinsic matrix
        distortion_coeffs: Camera distortion coefficients
        scaling_factors: Dictionary of scaling factors between spaces
        reference_points: Dictionary of known 3D-2D point correspondences
    """
    camera_matrix: np.ndarray
    distortion_coeffs: np.ndarray
    scaling_factors: dict[str, float]
    reference_points: dict[str, np.ndarray]


CoordinateSpace = typing.Literal['2d_image', '3d_model', 'real_world']


def transform_coordinates(
    point: np.ndarray,
    source_space: CoordinateSpace,
    target_space: CoordinateSpace,
    calibration_data: CalibrationData,
    wall_face: typing.Optional[WallFace] = None,
) -> np.ndarray:
    """Transform coordinates between different coordinate spaces.
    
    Args:
        point: Coordinates in source space (2D or 3D depending on space)
        source_space: Starting coordinate space
        target_space: Target coordinate space
        calibration_data: Calibration parameters for transformations
        wall_face: Wall face for transformations involving image space
    
    Returns:
        Transformed coordinates in target space
    
    Raises:
        ValueError: If source or target space is invalid or wall_face is missing when needed
    """
    # Validate input spaces
    valid_spaces = {'2d_image', '3d_model', 'real_world'}
    if source_space not in valid_spaces or target_space not in valid_spaces:
        raise ValueError(f"Invalid coordinate space. Must be one of {valid_spaces}")

    # Validate wall_face when needed
    if (source_space == '2d_image' or target_space == '2d_image') and wall_face is None:
        raise ValueError("Wall face must be provided for transformations involving image space")

    # Convert to homogeneous coordinates if needed
    if point.shape[0] == 2:
        point = np.append(point, 1)
    elif point.shape[0] == 3:
        point = np.append(point, 1)

    # Define transformation pipeline
    if source_space == target_space:
        return point[:-1]  # Remove homogeneous coordinate

    if source_space == '2d_image' and target_space == 'real_world':
        return _image_to_real_world(point, calibration_data, wall_face)
    
    if source_space == 'real_world' and target_space == '2d_image':
        return _real_world_to_image(point, calibration_data)
    
    if source_space == '3d_model' and target_space == 'real_world':
        # Apply scaling and any necessary rotations
        return _model_to_real_world(point, calibration_data)
    
    if source_space == 'real_world' and target_space == '3d_model':
        # Inverse of model to real world transformation
        return _real_world_to_model(point, calibration_data)
    
    # For transformations between 2d_image and 3d_model, go through real_world
    if source_space == '2d_image' and target_space == '3d_model':
        real_world = transform_coordinates(point, '2d_image', 'real_world', calibration_data)
        return transform_coordinates(real_world, 'real_world', '3d_model', calibration_data)
    
    if source_space == '3d_model' and target_space == '2d_image':
        real_world = transform_coordinates(point, '3d_model', 'real_world', calibration_data)
        return transform_coordinates(real_world, 'real_world', '2d_image', calibration_data)

    raise ValueError(f"Unsupported transformation from {source_space} to {target_space}")


def _image_to_real_world(
    point: np.ndarray, 
    calibration_data: CalibrationData,
    wall_face: WallFace
) -> np.ndarray:
    """Transform 2D image coordinates to 3D real-world coordinates.
    
    Uses camera calibration parameters and wall face geometry to estimate 3D position.
    Projects the point onto the specified wall face.
    
    Args:
        point: Homogeneous 2D point in image coordinates (x, y, 1)
        calibration_data: Camera calibration parameters and reference data
        wall_face: The wall face to project onto
    
    Returns:
        3D point in real-world coordinates (x, y, z)
    """
    # Undistort the point using camera parameters
    undistorted_point = cv2.undistortPoints(
        point[:2].reshape(1, 1, 2),
        calibration_data.camera_matrix,
        calibration_data.distortion_coeffs
    ).reshape(2)
    
    # Get camera pose from reference points
    _, rvec, tvec = cv2.solvePnP(
        calibration_data.reference_points['3d'],
        calibration_data.reference_points['2d'],
        calibration_data.camera_matrix,
        calibration_data.distortion_coeffs
    )
    
    # Convert rotation vector to matrix
    rotation_matrix, _ = cv2.Rodrigues(rvec)
    
    # Get camera position in world coordinates
    camera_position = -rotation_matrix.T @ tvec
    
    # Get ray direction in world coordinates
    ray_direction = rotation_matrix.T @ np.append(undistorted_point, 1.0)
    ray_direction = ray_direction / np.linalg.norm(ray_direction)
    
    # Compute intersection with wall face plane
    # Plane equation: dot(normal, (X - origin)) = 0
    # Ray equation: X = camera_position + t * ray_direction
    # Solve for t: dot(normal, (camera_position + t * ray_direction - origin)) = 0
    numerator = np.dot(wall_face.normal, (wall_face.origin - camera_position))
    denominator = np.dot(wall_face.normal, ray_direction)
    
    if abs(denominator) < 1e-6:  # Ray is parallel to plane
        raise ValueError("Unable to project point - ray is parallel to wall face")
    
    t = numerator / denominator
    
    if t < 0:  # Intersection is behind camera
        raise ValueError("Unable to project point - intersection is behind camera")
    
    # Compute intersection point
    intersection_point = camera_position + t * ray_direction
    
    return intersection_point


def _real_world_to_image(point: np.ndarray, calibration_data: CalibrationData) -> np.ndarray:
    """Transform 3D real-world coordinates to 2D image coordinates.
    
    Projects 3D point onto image plane using camera parameters.
    
    Args:
        point: Homogeneous 3D point in real-world coordinates (x, y, z, 1)
        calibration_data: Camera calibration parameters
    
    Returns:
        2D point in image coordinates (x, y)
    """
    # Get camera pose from reference points
    _, rvec, tvec = cv2.solvePnP(
        calibration_data.reference_points['3d'],
        calibration_data.reference_points['2d'],
        calibration_data.camera_matrix,
        calibration_data.distortion_coeffs
    )
    
    # Project 3D point to 2D
    image_point, _ = cv2.projectPoints(
        point[:3].reshape(1, 1, 3),
        rvec,
        tvec,
        calibration_data.camera_matrix,
        calibration_data.distortion_coeffs
    )
    
    return image_point.reshape(2)


def _model_to_real_world(point: np.ndarray, calibration_data: CalibrationData) -> np.ndarray:
    """Transform 3D model coordinates to real-world coordinates.
    
    Applies scaling and alignment transformations to convert from model space
    to real-world space.
    
    Args:
        point: Homogeneous 3D point in model coordinates (x, y, z, 1)
        calibration_data: Contains scaling factors and alignment data
    
    Returns:
        3D point in real-world coordinates (x, y, z)
    """
    # Extract scaling factors
    scale_x = calibration_data.scaling_factors.get('x', 1.0)
    scale_y = calibration_data.scaling_factors.get('y', 1.0)
    scale_z = calibration_data.scaling_factors.get('z', 1.0)
    
    # Create scaling matrix
    scaling_matrix = np.diag([scale_x, scale_y, scale_z, 1.0])
    
    # Apply scaling
    scaled_point = scaling_matrix @ point
    
    # If we have alignment reference points, compute and apply alignment transform
    if 'model' in calibration_data.reference_points and 'real' in calibration_data.reference_points:
        # Compute rigid transform between model and real-world reference points
        model_refs = calibration_data.reference_points['model']
        real_refs = calibration_data.reference_points['real']
        
        # Use Kabsch algorithm or similar to find optimal rigid transform
        rotation, translation = _compute_rigid_transform(model_refs, real_refs)
        
        # Apply transform
        transformed_point = (rotation @ scaled_point[:3]) + translation
        return transformed_point
    
    return scaled_point[:3]


def _real_world_to_model(point: np.ndarray, calibration_data: CalibrationData) -> np.ndarray:
    """Transform real-world coordinates to 3D model coordinates.
    
    Inverse of model_to_real_world transformation.
    
    Args:
        point: Homogeneous 3D point in real-world coordinates (x, y, z, 1)
        calibration_data: Contains scaling factors and alignment data
    
    Returns:
        3D point in model coordinates (x, y, z)
    """
    # Extract scaling factors
    scale_x = calibration_data.scaling_factors.get('x', 1.0)
    scale_y = calibration_data.scaling_factors.get('y', 1.0)
    scale_z = calibration_data.scaling_factors.get('z', 1.0)
    
    # Create inverse scaling matrix
    inv_scaling_matrix = np.diag([1/scale_x, 1/scale_y, 1/scale_z, 1.0])
    
    # If we have alignment reference points, compute and apply inverse alignment transform
    if 'model' in calibration_data.reference_points and 'real' in calibration_data.reference_points:
        model_refs = calibration_data.reference_points['model']
        real_refs = calibration_data.reference_points['real']
        
        # Compute inverse rigid transform
        rotation, translation = _compute_rigid_transform(real_refs, model_refs)
        
        # Apply inverse transform
        transformed_point = (rotation @ (point[:3] - translation))
        return inv_scaling_matrix @ np.append(transformed_point, 1)[:3]
    
    return (inv_scaling_matrix @ point)[:3]


def _compute_rigid_transform(points_a: np.ndarray, points_b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Compute optimal rigid transform between two sets of corresponding points.
    
    Uses Kabsch algorithm to find the best rigid transformation (rotation + translation)
    that maps points_a to points_b.
    
    Args:
        points_a: Nx3 array of points in source space
        points_b: Nx3 array of points in target space
    
    Returns:
        tuple of (3x3 rotation matrix, 3x1 translation vector)
    """
    # Center the points
    centroid_a = np.mean(points_a, axis=0)
    centroid_b = np.mean(points_b, axis=0)
    
    # Center the points
    centered_a = points_a - centroid_a
    centered_b = points_b - centroid_b
    
    # Compute optimal rotation
    H = centered_a.T @ centered_b
    U, _, Vt = np.linalg.svd(H)
    rotation = Vt.T @ U.T
    
    # Ensure right-handed coordinate system
    if np.linalg.det(rotation) < 0:
        Vt[-1, :] *= -1
        rotation = Vt.T @ U.T
    
    # Compute translation
    translation = centroid_b - rotation @ centroid_a
    
    return rotation, translation