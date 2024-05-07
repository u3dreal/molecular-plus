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
    for i in range(k):
        sq_dist += (point1[i] - point2[i]) * (point1[i] - point2[i])
    return sq_dist


cdef float dot_product(float u[3],float v[3])noexcept nogil:
    cdef float dot = 0
    dot = (u[0] * v[0]) + (u[1] * v[1]) + (u[2] * v[2])
    return dot


cdef void quick_sort(SParticle *a, int n, int axis)noexcept nogil:
    if (n < 2):
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