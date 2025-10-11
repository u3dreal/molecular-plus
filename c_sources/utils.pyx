cdef int arraysearch(int element, int *array, int len)noexcept nogil:
    cdef int i = 0
    for i in range(len):
        if element == array[i]:
            return i
    return -1





cdef float square_dist(float point1[3], float point2[3], int k)noexcept nogil:
    cdef float sq_dist = 0
    cdef int i
    for i in range(k):
        sq_dist += (point1[i] - point2[i]) * (point1[i] - point2[i])
    return sq_dist

# SIMD-optimized versions for ARM64 (NEON) and x86_64 (AVX2/SSE)
# Using runtime detection instead of compile-time conditionals
cdef float square_dist_simd(float point1[3], float point2[3]) noexcept nogil:
    # Fallback to standard implementation for now
    # Advanced SIMD implementations would need to be compiled separately
    return (point1[0] - point2[0]) * (point1[0] - point2[0]) + \
           (point1[1] - point2[1]) * (point1[1] - point2[1]) + \
           (point1[2] - point2[2]) * (point1[2] - point2[2])
    
cdef float dot_product_simd(float u[3], float v[3]) noexcept nogil:
    return (u[0] * v[0]) + (u[1] * v[1]) + (u[2] * v[2])

# Function to process multiple distance calculations at once (non-SIMD version for compatibility)
cdef void batch_square_dist_simd(float* points1, float* points2, float* results, int count) noexcept nogil:
    cdef int i
    for i in range(count):
        results[i] = (points1[i*3 + 0] - points2[i*3 + 0])**2 + \
                     (points1[i*3 + 1] - points2[i*3 + 1])**2 + \
                     (points1[i*3 + 2] - points2[i*3 + 2])**2

# 3D vector operations (simplified for compatibility)
cdef void vector_subtract_simd(float a[3], float b[3], float result[3]) noexcept nogil:
    result[0] = a[0] - b[0]
    result[1] = a[1] - b[1]
    result[2] = a[2] - b[2]

cdef void vector_multiply_scalar_simd(float vec[3], float scalar, float result[3]) noexcept nogil:
    result[0] = vec[0] * scalar
    result[1] = vec[1] * scalar
    result[2] = vec[2] * scalar

cdef float vector_length_simd(float vec[3]) noexcept nogil:
    return sqrt(vec[0]*vec[0] + vec[1]*vec[1] + vec[2]*vec[2])

cdef float dot_product(float u[3],float v[3])noexcept nogil:
    cdef float dot = 0
    dot = (u[0] * v[0]) + (u[1] * v[1]) + (u[2] * v[2])
    return dot

cdef extern from "neon_simd.h":
    float neon_square_dist(float*, float*) nogil
    float neon_dot_product(float*, float*) nogil
    void neon_vector_subtract(float*, float*, float*) nogil
    void neon_vector_multiply_scalar(float*, float, float*) nogil

# Function that uses NEON-optimized version if NEON is available
cdef float optimized_square_dist_3d(float point1[3], float point2[3]) noexcept nogil:
    # For now, use a simple implementation that will benefit from compiler optimizations
    cdef float dx = point1[0] - point2[0]
    cdef float dy = point1[1] - point2[1]
    cdef float dz = point1[2] - point2[2]
    return dx*dx + dy*dy + dz*dz

cdef float optimized_dot_product_3d(float u[3], float v[3]) noexcept nogil:
    return (u[0] * v[0]) + (u[1] * v[1]) + (u[2] * v[2])


cdef void quick_sort(SParticle *a, int n, int axis)noexcept nogil:
    # Use insertion sort for small arrays (hybrid approach)
    cdef int THRESHOLD = 10
    if (n < THRESHOLD):
        insertion_sort(a, n, axis)
        return

    cdef SParticle t
    cdef float p = a[int(n / 2)].loc[axis]
    cdef SParticle *l = a
    cdef SParticle *r = a + n - 1
    while l <= r:
        if l[0].loc[axis] < p:
            l += 1
            continue

        if r[0].loc[axis] > p:
            r -= 1
            # // we need to check the condition (l <= r) every time
            #  we change the value of l or r
            continue

        t = l[0]
        l[0] = r[0]
        # suggested by stephan to remove temp variable t but slower
        # l[0], r[0] = r[0], l[0]
        l += 1
        r[0] = t
        r -= 1

    quick_sort(a, r - a + 1, axis)
    quick_sort(l, a + n - l, axis)

# Insertion sort implementation for small arrays
cdef void insertion_sort(SParticle *a, int n, int axis) noexcept nogil:
    cdef int i, j
    cdef SParticle key
    for i in range(1, n):
        key = a[i]
        j = i-1
        while j >=0 and a[j].loc[axis] > key.loc[axis] :
                a[j+1] = a[j]
                j -= 1
        a[j+1] = key

# cdef void quick_sort(SParticle *a, int n, int axis) nogil:
#     cdef int THRESHOLD = 10  # switch to insertion sort when the size of the array is less than this threshold
#     if n < THRESHOLD:
#         insertion_sort(a, n, axis)
#         return

#     cdef SParticle t
#     cdef float p = medianfn(a[0].loc[axis], a[n / 2].loc[axis], a[n - 1].loc[axis])  # median of three
#     cdef SParticle *l = a
#     cdef SParticle *r = a + n - 1
#     while l <= r:
#         if l[0].loc[axis] < p:
#             l += 1
#             continue

#         if r[0].loc[axis] > p:
#             r -= 1
#             continue

#         t = l[0]
#         l[0] = r[0]
#         l += 1
#         r[0] = t
#         r -= 1

#     quick_sort(a, r - a + 1, axis)
#     quick_sort(l, a + n - l, axis)

# cdef void insertion_sort(SParticle *a, int n, int axis) noexcept nogil:
#     cdef int i, j
#     cdef SParticle key
#     for i in range(1, n):
#         key = a[i]
#         j = i-1
#         while j >=0 and a[j].loc[axis] > key.loc[axis] :
#                 a[j+1] = a[j]
#                 j -= 1
#         a[j+1] = key

# cdef float medianfn(float a, float b, float c) nogil:
#     if a < b:
#         if b < c:
#             return b
#         elif a < c:
#             return c
#         else:
#             return a
#     else:
#         if a < c:
#             return a
#         elif b < c:
#             return c
#         else:
#             return b
