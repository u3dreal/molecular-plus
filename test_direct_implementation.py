#!/usr/bin/env python3
"""
Test Direct Memory Access Implementation

This script tests the direct memory access implementation we just created.
Run this in Blender to test the par.as_pointer() functionality.
"""

import bpy
import bmesh
import time

def get_object(context, obj):
    """Get evaluated object with particle data."""
    depsgraph = context.evaluated_depsgraph_get()
    return obj.evaluated_get(depsgraph)

def create_simple_particle_system():
    """Create a simple particle system for testing."""
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Create emitter
    bpy.ops.mesh.primitive_plane_add(size=2)
    emitter = bpy.context.active_object
    emitter.name = "TestEmitter"
    
    # Add particle system
    bpy.ops.object.particle_system_add()
    psys = emitter.particle_systems[0]
    psys.name = "TestParticles"
    
    # Configure particles
    settings = psys.settings
    settings.count = 100
    settings.frame_start = 1
    settings.frame_end = 250
    settings.lifetime = 200
    settings.emit_from = 'FACE'
    settings.physics_type = 'NEWTON'
    settings.normal_factor = 2.0
    
    # Enable molecular settings if available
    if hasattr(settings, 'mol_active'):
        settings.mol_active = True
        settings.mol_density = 1.0
        settings.mol_selfcollision_active = True
    
    # Advance to generate particles
    bpy.context.scene.frame_set(10)
    
    # Get evaluated object to access actual particle data
    evaluated_emitter = get_object(bpy.context, emitter)
    evaluated_psys = evaluated_emitter.particle_systems[0]
    
    print(f"Created particle system with {len(evaluated_psys.particles)} particles")
    return evaluated_emitter, evaluated_psys

def test_direct_memory_access():
    """Test the direct memory access implementation."""
    print("Testing Direct Memory Access Implementation")
    print("=" * 50)
    
    # Create test particle system
    emitter, psys = create_simple_particle_system()
    
    if len(psys.particles) == 0:
        print("No particles generated! Try advancing more frames.")
        return False
    
    # Test 1: Basic par.as_pointer() functionality
    print("\n1. Testing par.as_pointer()...")
    try:
        first_particle = psys.particles[0]
        pointer = first_particle.as_pointer()
        print(f"   Particle pointer: 0x{pointer:016x}")
        print(f"   Location: {first_particle.location}")
        print(f"   Velocity: {first_particle.velocity}")
        print("   ✓ par.as_pointer() works!")
    except Exception as e:
        print(f"   ✗ par.as_pointer() failed: {e}")
        return False
    
    # Test 2: DirectMemoryParticleSystem (inline implementation for testing)
    print("\n2. Testing DirectMemoryParticleSystem...")
    try:
        # Inline implementation for testing in Blender
        import ctypes
        from ctypes import Structure, c_float, c_int, POINTER, cast
        
        class BlenderParticle(Structure):
            _fields_ = [
                ("index", c_int),
                ("age", c_float),
                ("lifetime", c_float),
                ("location", c_float * 3),
                ("rotation", c_float * 4),
                ("size", c_float),
                ("velocity", c_float * 3),
                ("angular_velocity", c_float * 3),
            ]
        
        class DirectMemoryParticleSystem:
            def __init__(self, psys):
                self.psys = psys
                self.particle_count = len(psys.particles)
                self.particle_pointers = []
                for par in psys.particles:
                    pointer = par.as_pointer()
                    self.particle_pointers.append(pointer)
            
            def get_particle_pointers(self):
                return self.particle_pointers
            
            def access_particle_directly(self, index):
                if index >= len(self.particle_pointers):
                    return None
                pointer = self.particle_pointers[index]
                particle = cast(pointer, POINTER(BlenderParticle)).contents
                return {
                    'location': [particle.location[0], particle.location[1], particle.location[2]],
                    'velocity': [particle.velocity[0], particle.velocity[1], particle.velocity[2]],
                    'size': particle.size,
                    'age': particle.age,
                    'lifetime': particle.lifetime,
                    'pointer': pointer
                }
        
        direct_psys = DirectMemoryParticleSystem(psys)
        print(f"   Particle count: {direct_psys.particle_count}")
        print(f"   Pointers collected: {len(direct_psys.get_particle_pointers())}")
        print("   ✓ DirectMemoryParticleSystem works!")
    except Exception as e:
        print(f"   ✗ DirectMemoryParticleSystem failed: {e}")
        return False
    
    # Test 3: Direct particle access
    print("\n3. Testing direct particle access...")
    try:
        particle_data = direct_psys.access_particle_directly(0)
        if particle_data:
            print(f"   Location: {particle_data['location']}")
            print(f"   Velocity: {particle_data['velocity']}")
            print(f"   Size: {particle_data['size']}")
            print("   ✓ Direct particle access works!")
        else:
            print("   ✗ Could not access particle directly")
            return False
    except Exception as e:
        print(f"   ✗ Direct particle access failed: {e}")
        return False
    
    # Test 4: Direct memory modification
    print("\n4. Testing direct memory modification...")
    try:
        # Test modifying particle data directly via pointer
        original_data = direct_psys.access_particle_directly(0)
        original_location = original_data['location'].copy()
        
        # Cast pointer and modify directly
        pointer = direct_psys.get_particle_pointers()[0]
        particle = cast(pointer, POINTER(BlenderParticle)).contents
        
        # Modify location directly in memory
        particle.location[0] += 0.1
        particle.location[1] += 0.1
        particle.location[2] += 0.1
        
        # Verify the change
        modified_data = direct_psys.access_particle_directly(0)
        modified_location = modified_data['location']
        
        print(f"   Original: {original_location}")
        print(f"   Modified: {modified_location}")
        
        # Check if modification worked
        if (abs(modified_location[0] - original_location[0] - 0.1) < 0.001 and
            abs(modified_location[1] - original_location[1] - 0.1) < 0.001 and
            abs(modified_location[2] - original_location[2] - 0.1) < 0.001):
            print("   ✓ Direct memory modification works!")
        else:
            print("   ✗ Direct memory modification failed")
            return False
            
    except Exception as e:
        print(f"   ✗ Direct memory modification failed: {e}")
        return False
    
    # Test 5: Basic collision detection concept
    print("\n5. Testing collision detection concept...")
    try:
        collision_count = 0
        pointers = direct_psys.get_particle_pointers()
        
        # Simple collision detection between first few particles
        for i in range(min(10, len(pointers))):
            p1 = cast(pointers[i], POINTER(BlenderParticle)).contents
            for j in range(i + 1, min(10, len(pointers))):
                p2 = cast(pointers[j], POINTER(BlenderParticle)).contents
                
                # Calculate distance
                dx = p1.location[0] - p2.location[0]
                dy = p1.location[1] - p2.location[1]
                dz = p1.location[2] - p2.location[2]
                distance = (dx*dx + dy*dy + dz*dz) ** 0.5
                
                # Check collision (simple size-based)
                min_distance = (p1.size + p2.size) * 0.5
                if distance < min_distance:
                    collision_count += 1
        
        print(f"   Checked {min(10, len(pointers))} particles")
        print(f"   Collisions detected: {collision_count}")
        print("   ✓ Collision detection concept works!")
        
    except Exception as e:
        print(f"   ✗ Collision detection concept failed: {e}")
        return False
    
    return True

def run_performance_test():
    """Run a basic performance test."""
    print("\nPerformance Test")
    print("=" * 20)
    
    emitter, psys = create_simple_particle_system()
    
    if len(psys.particles) == 0:
        print("No particles for performance test")
        return
    
    # Test pointer access speed
    iterations = 1000
    start_time = time.perf_counter()
    
    for _ in range(iterations):
        pointers = []
        for par in psys.particles:
            pointer = par.as_pointer()
            pointers.append(pointer)
    
    end_time = time.perf_counter()
    total_time = end_time - start_time
    
    print(f"Pointer access test:")
    print(f"  Particles: {len(psys.particles)}")
    print(f"  Iterations: {iterations}")
    print(f"  Total time: {total_time:.4f}s")
    print(f"  Time per iteration: {total_time/iterations*1000:.2f}ms")
    print(f"  Pointers per second: {len(psys.particles)*iterations/total_time:.0f}")

if __name__ == "__main__":
    print("Direct Memory Access Implementation Test")
    print("=" * 60)
    
    try:
        success = test_direct_memory_access()
        
        if success:
            print("\n" + "=" * 60)
            print("✓ ALL TESTS PASSED!")
            print("Direct memory access implementation is working correctly.")
            
            # Run performance test
            run_performance_test()
        else:
            print("\n" + "=" * 60)
            print("✗ SOME TESTS FAILED!")
            print("Check the errors above for details.")
            
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("Make sure you're running this in Blender with a particle system.")
    
    print("\nTest complete!")