#!/usr/bin/env python3
"""
Test Direct Memory Access Implementation

This script tests the direct memory access implementation we just created.
Run this in Blender to test the par.as_pointer() functionality.
"""

import bpy
import bmesh
import time

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
    
    print(f"Created particle system with {len(psys.particles)} particles")
    return emitter, psys

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
    
    # Test 2: DirectMemoryParticleSystem
    print("\n2. Testing DirectMemoryParticleSystem...")
    try:
        from addon.simulate_direct import DirectMemoryParticleSystem
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
    
    # Test 4: pack_data_direct
    print("\n4. Testing pack_data_direct...")
    try:
        from addon.simulate_direct import pack_data_direct
        direct_data = pack_data_direct(bpy.context, True)
        print(f"   Systems found: {len(direct_data['systems'])}")
        print(f"   Total particles: {direct_data['total_particles']}")
        print("   ✓ pack_data_direct works!")
    except Exception as e:
        print(f"   ✗ pack_data_direct failed: {e}")
        return False
    
    # Test 5: Cython simulation (if available)
    print("\n5. Testing Cython simulation...")
    try:
        from addon.simulate_direct import simulate_direct
        results = simulate_direct(direct_data)
        print(f"   Results: {results}")
        if results:
            result = results[0]
            print(f"   Particles processed: {result['particle_count']}")
            print(f"   Collisions resolved: {result['collisions_resolved']}")
            print(f"   Links processed: {result['links_processed']}")
            print("   ✓ Cython simulation works!")
        else:
            print("   ✗ No simulation results")
            return False
    except Exception as e:
        print(f"   ✗ Cython simulation failed: {e}")
        print("   (This is expected if Cython module isn't compiled)")
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