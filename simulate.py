import bpy
import array
import numpy as np
from .utils import get_object


def get_gn_float_attr(obj, mod_name, attr_name, weak_map):
    # Find target modifier index
    for target_idx, mod in enumerate(obj.modifiers):
        if mod.name == mod_name:
            break
    else:
        raise ValueError(f"Modifier '{mod_name}' not found")

    print("start bake weakmap from geo nodes: ", mod.name)

    # Temporarily disable modifiers after target
    orig_states = [(mod, mod.show_viewport) for mod in obj.modifiers[target_idx + 1 :]]
    for mod, _ in orig_states:
        mod.show_viewport = False

    # Force depsgraph to re-evaluate without those modifiers
    obj.update_tag()  # ← Critical!
    bpy.context.view_layer.update()

    try:
        # Evaluate and read FLOAT attribute directly into weak_map
        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(depsgraph)
        mesh = eval_obj.data

        attr = mesh.attributes.get(attr_name)

        print("attributes: " + str(len(attr.data)))
        print("np_array: " + str(len(weak_map)))

        if len(attr.data) != len(weak_map):
            raise ValueError("Attribute and weak_map lengths do not match !")

        attr.data.foreach_get("value", weak_map)
    finally:
        # Restore modifier states
        for mod, state in orig_states:
            mod.show_viewport = state


def get_weak_map(obj, psys, par_weak):
    print("start bake weakmap from:", obj.name)

    tex = psys.settings.texture_slots[0].texture
    texm_offset = psys.settings.texture_slots[0].offset
    texm_scale = psys.settings.texture_slots[0].scale
    parlen = len(psys.particles)
    colramp = tex.color_ramp

    for i in range(parlen):
        newuv = (
            (psys.particles[i].location + texm_offset) @ obj.matrix_world * texm_scale
        )
        if tex.use_color_ramp:
            par_weak[i] = colramp.evaluate(tex.evaluate(newuv)[0])[0]
        else:
            par_weak[i] = tex.evaluate(newuv)[0]

        if psys.settings.mol_inv_weak_map:
            par_weak[i] = 1 - par_weak[i]

    print("Weakmap baked on:", psys.settings.name)


def pack_data(context, initiate):
    psyslen = 0
    parnum = 0
    scene = context.scene

    for ob in bpy.data.objects:
        obj = get_object(context, ob)

        for i, psys in enumerate(obj.particle_systems):
            if psys.settings.mol_matter != "-1":
                psys.settings.mol_density = float(psys.settings.mol_matter)

            parlen = len(psys.particles)

            if psys.settings.mol_active and parlen:
                par_loc = array.array("f", [0, 0, 0]) * parlen
                par_vel = array.array("f", [0, 0, 0]) * parlen
                par_size = array.array("f", [0]) * parlen
                par_alive = array.array("h", [0]) * parlen

                parnum += parlen

                psys.particles.foreach_get("location", par_loc)
                psys.particles.foreach_get("velocity", par_vel)
                psys.particles.foreach_get("alive_state", par_alive)

                if initiate:
                    par_mass = array.array("f", [0]) * parlen

                    psys.particles.foreach_get("size", par_size)

                    # use texture in slot 0 for particle weak
                    par_weak = array.array("f", [1.0]) * parlen

                    if psys.settings.mol_bake_weak_map_geo:
                        get_gn_float_attr(ob, "M+ weak map", "weak_map", par_weak)
                        # Force depsgraph to re-evaluate with modifiers reenabled
                        ob.update_tag()  # ← Critical!
                        bpy.context.view_layer.update()
                        obj = get_object(context, ob)
                        psys = obj.particle_systems[i]

                    if psys.settings.mol_bake_weak_map:
                        get_weak_map(obj, psys, par_weak)

                    if psys.settings.mol_density_active:
                        par_mass_np = np.asarray(par_mass)
                        par_size_np = np.asarray(par_size)
                        par_mass_np[:] = psys.settings.mol_density * (
                            4 / 3 * 3.141592653589793 * ((par_size_np / 2) ** 3)
                        )
                        par_mass = par_mass_np

                    else:
                        par_mass = array.array("f", [psys.settings.mass]) * parlen

                    if scene.timescale != 1.0:
                        psys.settings.timestep = 1 / (
                            scene.render.fps / scene.timescale
                        )
                    else:
                        psys.settings.timestep = 1 / scene.render.fps

                    psyslen += 1

                    if bpy.context.scene.mol_minsize > min(par_size):
                        bpy.context.scene.mol_minsize = min(par_size)

                    if psys.settings.mol_link_samevalue:
                        psys.settings.mol_link_estiff = psys.settings.mol_link_stiff
                        psys.settings.mol_link_estiffrand = (
                            psys.settings.mol_link_stiffrand
                        )
                        psys.settings.mol_link_estiffexp = (
                            psys.settings.mol_link_stiffexp
                        )
                        psys.settings.mol_link_edamp = psys.settings.mol_link_damp
                        psys.settings.mol_link_edamprand = (
                            psys.settings.mol_link_damprand
                        )
                        psys.settings.mol_link_ebroken = psys.settings.mol_link_broken
                        psys.settings.mol_link_ebrokenrand = (
                            psys.settings.mol_link_brokenrand
                        )

                    if psys.settings.mol_relink_samevalue:
                        psys.settings.mol_relink_estiff = psys.settings.mol_relink_stiff
                        psys.settings.mol_relink_estiffrand = (
                            psys.settings.mol_relink_stiffrand
                        )
                        psys.settings.mol_relink_estiffexp = (
                            psys.settings.mol_relink_stiffexp
                        )
                        psys.settings.mol_relink_edamp = psys.settings.mol_relink_damp
                        psys.settings.mol_relink_edamprand = (
                            psys.settings.mol_relink_damprand
                        )
                        psys.settings.mol_relink_ebroken = (
                            psys.settings.mol_relink_broken
                        )
                        psys.settings.mol_relink_ebrokenrand = (
                            psys.settings.mol_relink_brokenrand
                        )

                    params = [0] * 48

                    params[0] = psys.settings.mol_selfcollision_active
                    params[1] = psys.settings.mol_othercollision_active
                    params[2] = psys.settings.mol_collision_group
                    params[3] = psys.settings.mol_friction
                    params[4] = psys.settings.mol_collision_damp
                    params[5] = psys.settings.mol_links_active
                    params[6] = psys.settings.mol_link_length
                    params[7] = psys.settings.mol_link_max
                    params[8] = psys.settings.mol_link_tension
                    params[9] = psys.settings.mol_link_tensionrand
                    params[10] = psys.settings.mol_link_stiff
                    params[11] = psys.settings.mol_link_stiffrand
                    params[12] = psys.settings.mol_link_stiffexp
                    params[13] = psys.settings.mol_link_damp
                    params[14] = psys.settings.mol_link_damprand
                    params[15] = psys.settings.mol_link_broken
                    params[16] = psys.settings.mol_link_brokenrand
                    params[17] = psys.settings.mol_link_estiff
                    params[18] = psys.settings.mol_link_estiffrand
                    params[19] = psys.settings.mol_link_estiffexp
                    params[20] = psys.settings.mol_link_edamp
                    params[21] = psys.settings.mol_link_edamprand
                    params[22] = psys.settings.mol_link_ebroken
                    params[23] = psys.settings.mol_link_ebrokenrand
                    params[24] = psys.settings.mol_relink_group
                    params[25] = psys.settings.mol_relink_chance
                    params[26] = psys.settings.mol_relink_chancerand
                    params[27] = psys.settings.mol_relink_max
                    params[28] = psys.settings.mol_relink_tension
                    params[29] = psys.settings.mol_relink_tensionrand
                    params[30] = psys.settings.mol_relink_stiff
                    params[31] = psys.settings.mol_relink_stiffexp
                    params[32] = psys.settings.mol_relink_stiffrand
                    params[33] = psys.settings.mol_relink_damp
                    params[34] = psys.settings.mol_relink_damprand
                    params[35] = psys.settings.mol_relink_broken
                    params[36] = psys.settings.mol_relink_brokenrand
                    params[37] = psys.settings.mol_relink_estiff
                    params[38] = psys.settings.mol_relink_estiffexp
                    params[39] = psys.settings.mol_relink_estiffrand
                    params[40] = psys.settings.mol_relink_edamp
                    params[41] = psys.settings.mol_relink_edamprand
                    params[42] = psys.settings.mol_relink_ebroken
                    params[43] = psys.settings.mol_relink_ebrokenrand
                    params[44] = psys.settings.mol_link_friction
                    params[45] = psys.settings.mol_link_group
                    params[46] = psys.settings.mol_other_link_active
                    params[47] = int(psys.settings.mol_link_rellength)
                    params[48] = psys.settings.mol_collison_adhesion_search_distance
                    params[49] = psys.settings.mol_collison_adhesion_factor

                mol_exportdata = bpy.context.scene.mol_exportdata

                if initiate:
                    mol_exportdata[0][2] = psyslen
                    mol_exportdata[0][3] = parnum
                    mol_exportdata.append(
                        (
                            parlen,
                            par_loc,
                            par_vel,
                            par_size,
                            par_mass,
                            par_alive,
                            params,
                            par_weak,
                        )
                    )
                else:
                    self_coll = psys.settings.mol_selfcollision_active
                    mol_exportdata.append((par_loc, par_vel, par_alive, self_coll))
