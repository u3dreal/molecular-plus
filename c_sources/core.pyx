#cython: profile=False
#cython: boundscheck=False
#cython: wraparound=False
#cython: cdivision=True
#cython: language_level=3
#cython: cpow=True

# NOTE: order of slow functions to be optimize/multithreaded:
# kdtreesearching, kdtreecreating, linksolving