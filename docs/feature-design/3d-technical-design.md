# 3D Model Integration Technical Design

## Overview

This document outlines the technical design for integrating 3D model visualization into the BetaBoard system, with particular focus on mapping between 2D and 3D coordinate systems.

## Core Challenges

### 1. Coordinate System Management

The system must handle multiple coordinate spaces:
- 2D image space (pixels)
- 3D model space (meters/units)
- Real-world space (meters)

#### Solution Approach

1. **Common Reference Frame**
   - Define global coordinate system:
     - Origin at bottom-left corner of main wall
     - Y axis points directly up (gravity-aligned)
     - X axis points horizontally right when facing the wall
     - Z axis follows right-hand rule (generally pointing into the climbing space)

2. **Wall Face Transformations**
   ```python
   class WallFace(dataclasses.dataclass):
       """Represents a planar section of the climbing wall."""
       normal: np.ndarray  # Normal vector to the face
       origin: np.ndarray  # Point where face meets the ground
       rotation: np.ndarray  # Rotation matrix from global to face coordinates
   ```

3. **Hold Position and Force Vector Management**
   ```python
   class Hold(dataclasses.dataclass):
       """Represents a climbing hold with position and force data."""
       position: np.ndarray  # Global coordinates
       face: WallFace  # Which wall face the hold belongs to
       
       def transform_force_vector(self, force: np.ndarray) -> np.ndarray:
           """
           Transform force vector from hold's face coordinates to global coordinates.
           
           Args:
               force: Force vector in face-local coordinates (normal to face)
           
           Returns:
               Force vector in global coordinates
           """
           return self.face.rotation @ force
   ```

4. **Transformation Pipeline**
   ```python
   def transform_coordinates(
       point: np.ndarray,
       source_space: str,
       target_space: str,
       calibration_data: CalibrationData,
       wall_face: Optional[WallFace] = None
   ) -> np.ndarray:
       """
       Transform coordinates between different spaces.
       
       Args:
           point: Coordinates in source space
           source_space: One of ['2d_image', '3d_model', 'real_world']
           target_space: One of ['2d_image', '3d_model', 'real_world']
           calibration_data: Camera parameters, scaling factors, etc.
           wall_face: Optional wall face for force vector transformations
       
       Returns:
           Transformed coordinates in target space
       """
   ```

### 2. Camera Parameter Extraction

Extract camera parameters to align 3D view with 2D photos.

#### Solution Approach

1. **OpenCV Calibration**
   - Use checkerboard patterns for initial camera calibration
   - Store camera intrinsics for different camera types (Pi Camera, smartphone)
   - Extract extrinsics from wall corners or known reference points

2. **Three.js Camera Setup**
   ```typescript
   interface CameraParams {
     position: [number, number, number];
     rotation: [number, number, number];
     fov: number;
     aspect: number;
   }

   function setupCamera(params: CameraParams): THREE.PerspectiveCamera {
     // Convert OpenCV camera parameters to Three.js camera setup
   }
   ```

### 3. Hold Position Mapping

Map hold positions between 2D and 3D spaces.

#### Solution Approach

1. **Direct Linear Transformation (DLT)**
   ```python
   def compute_dlt_matrix(image_points: np.ndarray, 
                         model_points: np.ndarray) -> np.ndarray:
       """
       Compute DLT matrix from corresponding points.
       
       Args:
           image_points: Nx2 array of 2D points
           model_points: Nx3 array of 3D points
       
       Returns:
           3x4 projection matrix
       """
   ```

2. **Reference Point Detection**
   - Use board corner detection in both 2D and 3D
   - Store reference points for future use

### 4. Force Vector Visualization

Display force sensor data in 3D space, accounting for wall geometry.

#### Solution Approach

1. **Vector Data Structure**
   ```typescript
   interface ForceVector {
     position: [number, number, number];  // Hold position in global coordinates
     force: [number, number, number];     // Force components in global coordinates
     faceNormal: [number, number, number]; // Normal vector of wall face at hold
     timestamp: number;
   }
   ```

2. **Force Transformation**
   ```python
   def transform_force_to_global(
       force: np.ndarray,
       face_normal: np.ndarray,
       face_rotation: np.ndarray
   ) -> np.ndarray:
       """
       Transform force vector from face-local to global coordinates.
       
       Args:
           force: Force vector in face-local coordinates
           face_normal: Normal vector of the wall face
           face_rotation: Rotation matrix for the wall face
       
       Returns:
           Force vector in global coordinates
       """
   ```

3. **Rendering Component**
   ```typescript
   function ForceVectors({ 
     data: ForceVector[],
     scale: number,
     colorMap: (magnitude: number) => string 
   }) {
     // Transform vectors to global space before rendering
     // Render using Three.js ArrowHelper
   }
   ```

### 5. Climber Pose Integration

Combine monocular 3D pose estimation with hold position constraints.

#### Solution Approach

1. **Pose Estimation Pipeline**
   ```python
   def estimate_3d_pose(
       video_frame: np.ndarray,
       known_holds: List[Point3D],
       contact_points: List[ContactPoint],
   ) -> Pose3D:
       """
       Estimate 3D pose using video frame and known constraints.
       
       Args:
           video_frame: Current video frame
           known_holds: 3D positions of holds
           contact_points: Known body-hold contact points
       
       Returns:
           3D pose estimation
       """
   ```

2. **Constraint Application**
   - Use hold positions as anchor points for hands/feet
   - Apply physical constraints (limb lengths, joint angles)
   - Smooth transitions between frames

## Implementation Phases

### Phase 1: Coordinate System Foundation
1. Implement coordinate transformation pipeline
2. Set up camera parameter extraction
3. Create basic 3D visualization

### Phase 2: Hold Mapping
1. Implement DLT-based mapping
2. Add reference point detection
3. Create hold position visualization

### Phase 3: Force Visualization
1. Implement force vector rendering
2. Add time-based animation
3. Integrate with existing sensor data

### Phase 4: Pose Integration
1. Implement basic pose estimation
2. Add hold position constraints
3. Create pose visualization

## Technical Considerations

### Performance
- Three.js for efficient 3D rendering
- Frame rate limiting for animations
- Optimize data structures for real-time updates

## Dependencies

- **Three.js**: 3D rendering
- **OpenCV**: Camera calibration and computer vision
- **TensorFlow.js**: Pose estimation
- **React Three Fiber**: React bindings for Three.js

## Future Considerations

1. **Multiple Camera Support**
   - Handle multiple viewpoints
   - Combine data from different angles

2. **Advanced Pose Estimation**
   - Implement multi-view pose estimation
   - Improve accuracy with additional sensors