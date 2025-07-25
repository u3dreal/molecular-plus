#!/usr/bin/env python3
"""
Benchmark script for testing molecular particle solver performance
"""

import time
import sys
import os
import statistics
from typing import List, Tuple

def benchmark_simulation(simulate_func, data, iterations: int = 5) -> Tuple[float, float, List[float]]:
    """
    Benchmark the simulation function
    
    Args:
        simulate_func: The simulation function to benchmark
        data: Input data for simulation
        iterations: Number of iterations to run
    
    Returns:
        Tuple of (mean_time, std_dev, all_times)
    """
    times = []
    
    print(f"Running {iterations} benchmark iterations...")
    
    for i in range(iterations):
        start_time = time.perf_counter()
        result = simulate_func(data)
        end_time = time.perf_counter()
        
        iteration_time = end_time - start_time
        times.append(iteration_time)
        
        print(f"Iteration {i+1}: {iteration_time:.4f}s")
    
    mean_time = statistics.mean(times)
    std_dev = statistics.stdev(times) if len(times) > 1 else 0.0
    
    return mean_time, std_dev, times

def compare_implementations(old_simulate, new_simulate, data, iterations: int = 5):
    """
    Compare performance between old and new implementations
    """
    print("=" * 60)
    print("MOLECULAR PARTICLE SOLVER BENCHMARK")
    print("=" * 60)
    
    # Benchmark original implementation
    print("\nBenchmarking ORIGINAL implementation:")
    old_mean, old_std, old_times = benchmark_simulation(old_simulate, data, iterations)
    
    # Benchmark optimized implementation  
    print("\nBenchmarking OPTIMIZED implementation:")
    new_mean, new_std, new_times = benchmark_simulation(new_simulate, data, iterations)
    
    # Calculate improvement
    improvement = ((old_mean - new_mean) / old_mean) * 100
    speedup = old_mean / new_mean
    
    # Print results
    print("\n" + "=" * 60)
    print("BENCHMARK RESULTS")
    print("=" * 60)
    print(f"Original Implementation:")
    print(f"  Mean time:     {old_mean:.4f}s ± {old_std:.4f}s")
    print(f"  Min time:      {min(old_times):.4f}s")
    print(f"  Max time:      {max(old_times):.4f}s")
    
    print(f"\nOptimized Implementation:")
    print(f"  Mean time:     {new_mean:.4f}s ± {new_std:.4f}s")
    print(f"  Min time:      {min(new_times):.4f}s")
    print(f"  Max time:      {max(new_times):.4f}s")
    
    print(f"\nPerformance Improvement:")
    print(f"  Speed improvement: {improvement:+.1f}%")
    print(f"  Speedup factor:    {speedup:.2f}x")
    
    if improvement > 0:
        print(f"  🚀 OPTIMIZED version is {improvement:.1f}% FASTER!")
    else:
        print(f"  ⚠️  OPTIMIZED version is {abs(improvement):.1f}% slower")
    
    return {
        'old_mean': old_mean,
        'new_mean': new_mean,
        'improvement': improvement,
        'speedup': speedup
    }

def create_test_data(particle_count: int = 1000):
    """
    Create test data for benchmarking
    Adjust this based on your actual data format
    """
    # This is a placeholder - you'll need to adapt this to your actual data format
    print(f"Creating test data for {particle_count} particles...")
    
    # Example data structure - modify based on your actual format
    test_data = [
        [24.0, 0, 1, particle_count, 4],  # fps, substep, psysnum, parnum, cpunum
        # Add particle system data here based on your format
    ]
    
    return test_data

def main():
    """
    Main benchmark function
    """
    if len(sys.argv) > 1:
        particle_count = int(sys.argv[1])
    else:
        particle_count = 1000
    
    print(f"Molecular Particle Solver Benchmark")
    print(f"Particle count: {particle_count}")
    
    # Create test data
    data = create_test_data(particle_count)
    
    try:
        # Import both versions if available
        print("Attempting to import simulation modules...")
        
        # You'll need to modify these imports based on your actual module structure
        # from molecular_core_old import core as old_core
        # from molecular_core import core as new_core
        
        # For now, we'll just show how to use the benchmark functions
        print("To use this benchmark:")
        print("1. Import your old and new simulation functions")
        print("2. Call compare_implementations(old_func, new_func, data)")
        print("3. Review the performance results")
        
        # Example usage:
        # results = compare_implementations(
        #     old_core.simulate, 
        #     new_core.simulate, 
        #     data, 
        #     iterations=5
        # )
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure both old and new versions are compiled and available")

if __name__ == "__main__":
    main()