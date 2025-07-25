cdef int arraysearch(int element, int *array, int len)noexcept nogil:
    cdef int i = 0
    for i in range(len):
        if element == array[i]:
            return i
    return -1


cdef float fabs(float value)noexcept nogil:
    if value >= 0:
        return value
    if value < 0:
        return -value


#@cython.cdivision(True)
cdef float square_dist(float point1[3], float point2[3], int k)noexcept nogil:
    cdef float sq_dist = 0
    cdef int i
    cdef float dx, dy, dz
    # Unroll loop for common case k=3 (3D space)
    if k == 3:
        dx = point1[0] - point2[0]
        dy = point1[1] - point2[1]
        dz = point1[2] - point2[2]
        return dx*dx + dy*dy + dz*dz
    else:
        for i in range(k):
            sq_dist += (point1[i] - point2[i]) * (point1[i] - point2[i])
        return sq_dist


cdef float dot_product(float u[3],float v[3])noexcept nogil:
    # Direct computation is faster than loop for 3D vectors
    return (u[0] * v[0]) + (u[1] * v[1]) + (u[2] * v[2])

# Fast inverse square root approximation (Quake III algorithm)
cdef float fast_inv_sqrt(float x)noexcept nogil:
    if x <= 0:
        return 0
    # For modern CPUs, regular 1/sqrt(x) is often faster due to hardware optimization
    # But we keep this for reference and potential future use
    return 1.0 / sqrt(x)

# Optimized array search with early termination
cdef int fast_arraysearch(int element, int *array, int len)noexcept nogil:
    cdef int i = 0
    # Unroll first few iterations for better branch prediction
    if len > 0 and array[0] == element:
        return 0
    if len > 1 and array[1] == element:
        return 1
    if len > 2 and array[2] == element:
        return 2
    if len > 3 and array[3] == element:
        return 3
    
    # Continue with regular loop for remaining elements
    for i in range(4, len):
        if element == array[i]:
            return i
    return -1


cdef void insertion_sort(SParticle *a, int n, int axis)noexcept nogil:
    cdef int i, j
    cdef SParticle key
    for i in range(1, n):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j].loc[axis] > key.loc[axis]:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key

cdef float median_of_three(float a, float b, float c)noexcept nogil:
    if a <= b <= c or c <= b <= a:
        return b
    elif b <= a <= c or c <= a <= b:
        return a
    else:
        return c

cdef void quick_sort(SParticle *a, int n, int axis)noexcept nogil:
    cdef int THRESHOLD = 16  # Use insertion sort for small arrays
    if n < THRESHOLD:
        insertion_sort(a, n, axis)
        return
    if n < 2:
        return
        
    cdef SParticle t
    # Median-of-three pivot selection for better performance
    cdef float p = median_of_three(a[0].loc[axis], a[n//2].loc[axis], a[n-1].loc[axis])
    cdef SParticle *l = a
    cdef SParticle *r = a + n - 1
    
    while l <= r:
        while l[0].loc[axis] < p:
            l += 1
        while r[0].loc[axis] > p:
            r -= 1
        if l <= r:
            t = l[0]
            l[0] = r[0]
            r[0] = t
            l += 1
            r -= 1

    # Tail recursion optimization - recurse on smaller partition first
    if (r - a + 1) < (a + n - l):
        quick_sort(a, r - a + 1, axis)
        quick_sort(l, a + n - l, axis)
    else:
        quick_sort(l, a + n - l, axis)
        quick_sort(a, r - a + 1, axis)

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