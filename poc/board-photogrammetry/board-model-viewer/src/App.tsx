import { Canvas } from '@react-three/fiber'
import { useEffect, useState } from 'react'
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader'
import { MTLLoader } from 'three/examples/jsm/loaders/MTLLoader'
import { OrbitControls, PerspectiveCamera } from '@react-three/drei'
import * as THREE from 'three'

function Model() {
  const [model, setModel] = useState<THREE.Group | null>(null)

  useEffect(() => {
    const mtlLoader = new MTLLoader()
    
    mtlLoader.load(
      '/models/scene_mesh_textured.mtl',
      (materials) => {
        materials.preload()
        
        const objLoader = new OBJLoader()
        objLoader.setMaterials(materials)
        
        objLoader.load(
          '/models/scene_mesh_textured.obj',
          (object) => {
            object.traverse((child) => {
              if (child instanceof THREE.Mesh && child.material) {
                child.material.transparent = false
                child.material.opacity = 1.0
                child.material.side = THREE.DoubleSide
                child.material.needsUpdate = true
                
                if (child.material.map) {
                  child.material.map.needsUpdate = true
                }
              }
            })

            const box = new THREE.Box3().setFromObject(object)
            const center = box.getCenter(new THREE.Vector3())
            
            object.position.set(-center.x, -center.y, -center.z)
            
            object.scale.multiplyScalar(5.0)
            object.rotation.x = -Math.PI / 2
            
            setModel(object)
          },
          undefined,
          (error) => {
            console.error('Error loading model:', error)
          }
        )
      },
      undefined,
      (error) => {
        console.error('Error loading MTL:', error)
      }
    )
  }, [])

  return model ? <primitive object={model} /> : null
}

function App() {
  return (
    <div style={{ width: '100vw', height: '100vh', background: '#333' }}>
      <Canvas>
        <PerspectiveCamera makeDefault position={[5, 5, 5]} />
        
        <ambientLight intensity={1.0} />
        <directionalLight position={[5, 5, 5]} intensity={2} />
        <directionalLight position={[-5, -5, -5]} intensity={1} />
        <pointLight position={[0, 5, 0]} intensity={1} />
        
        <gridHelper args={[20, 20]} />
        
        <Model />
        
        <OrbitControls 
          enableDamping={false}
          enableZoom={true}
          enablePan={true}
          minDistance={1}
          maxDistance={20}
        />
      </Canvas>
    </div>
  )
}

export default App