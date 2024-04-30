cdef void update(data):
    global parlist
    global parnum
    global psysnum
    global psys

    cdef int i = 0
    cdef int ii = 0

    for i in range(psysnum):
        psys[i].selfcollision_active = data[i][3]
        
        for ii in range(psys[i].parnum):

            psys[i].particles[ii].loc[0] = data[i][0][(ii * 3)]
            psys[i].particles[ii].loc[1] = data[i][0][(ii * 3) + 1]
            psys[i].particles[ii].loc[2] = data[i][0][(ii * 3) + 2]
            psys[i].particles[ii].vel[0] = data[i][1][(ii * 3)]
            psys[i].particles[ii].vel[1] = data[i][1][(ii * 3) + 1]
            psys[i].particles[ii].vel[2] = data[i][1][(ii * 3) + 2]

            if psys[i].particles[ii].state == 3 and data[i][2][ii] == 3:
                psys[i].particles[ii].state = data[i][2][ii] + 1
                if psys[i].links_active == 1:
                    if psys[i].link_rellength == 1:
                        KDTree_rnn_query(
                            kdtree,
                            &psys[i].particles[ii],
                            psys[i].particles[ii].loc,
                            psys[i].particles[ii].size * psys[i].particles[ii].sys.link_length
                        )
                    else:
                        KDTree_rnn_query(
                            kdtree,
                            &psys[i].particles[ii],
                            psys[i].particles[ii].loc,
                            psys[i].particles[ii].sys.link_length
                        )
                    create_link(psys[i].particles[ii].id, psys[i].link_max)
                    # free(psys[i].particles[ii].neighbours)
                    psys[i].particles[ii].neighboursnum = 0

            elif psys[i].particles[ii].state == 4 and data[i][2][ii] == 3:
                psys[i].particles[ii].state = 4

            else:
                psys[i].particles[ii].state = data[i][2][ii]

            psys[i].particles[ii].collided_with = <int *>realloc(
                psys[i].particles[ii].collided_with,
                1 * cython.sizeof(int)
            )
            psys[i].particles[ii].collided_num = 0