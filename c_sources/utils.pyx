cdef int arraysearch(int element, int *array, int len)noexcept nogil:
    cdef int i = 0
    for i in range(len):
        if element == array[i]:
            return i
    return -1





#@cython.cdivision(True)
cdef float square_dist(float point1[3], float point2[3], int k)noexcept nogil:
    cdef float sq_dist = 0
    cdef int i
    for i in range(k):
        sq_dist += (point1[i] - point2[i]) * (point1[i] - point2[i])
    return sq_dist

cdef float optimized_square_dist_3d(float point1[3], float point2[3]) noexcept nogil:
    # For now, use a simple implementation that will benefit from compiler optimizations
    cdef float dx = point1[0] - point2[0]
    cdef float dy = point1[1] - point2[1]
    cdef float dz = point1[2] - point2[2]
    return dx*dx + dy*dy + dz*dz

cdef float dot_product(float u[3],float v[3])noexcept nogil:
    cdef float dot = 0
    dot = (u[0] * v[0]) + (u[1] * v[1]) + (u[2] * v[2])
    return dot


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
