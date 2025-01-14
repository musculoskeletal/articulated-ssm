import numpy as np
from gias3.visualisation import fieldvi
import os


def plot_acs_per_bone(origin, x, y, z, node_coords):
    i_vec = np.zeros((100, 3))
    j_vec = np.zeros((100, 3))
    k_vec = np.zeros((100, 3))

    for i in range(0, 100):
        i_vec[i, :] = origin + (i * 1 * x)
        j_vec[i, :] = origin + (i * 1 * y)
        k_vec[i, :] = origin + (i * 1 * z)

    v = fieldvi.FieldVi()
    v.addData('nodes', node_coords, render_args={'mode': 'sphere', 'scale_factor': 1.0, 'color': (0, 1, 1)})
    v.addData('I', i_vec, render_args={'mode': 'sphere', 'scale_factor': 1.0, 'color': (1, 0, 0)})
    v.addData('J', j_vec, render_args={'mode': 'sphere', 'scale_factor': 1.0, 'color': (0, 1, 0)})
    v.addData('K', k_vec, render_args={'mode': 'sphere', 'scale_factor': 1.0, 'color': (0, 0, 1)})
    v.configure_traits()


def plot_all_bones_one_side(ll_model_side):
    if ll_model_side.include_patella == 1:
        node_coords = np.vstack((ll_model_side.femur_model.node_coords, ll_model_side.tibfib_model.node_coords,
                                 ll_model_side.pelvis_model.node_coords, ll_model_side.patella_model.node_coords))
    else:
        node_coords = np.vstack((ll_model_side.femur_model.node_coords, ll_model_side.tibfib_model.node_coords,
                                 ll_model_side.pelvis_model.node_coords))

    v = fieldvi.FieldVi()
    bone_meshes = ll_model_side.ssm_handler.obtain_mesh_from_point_cloud(node_coords)
    v.addTri('bone_meshes', bone_meshes, render_args={'mode': 'sphere', 'scale_factor': 1.0, 'color': (1, 1, 1)})

    if ll_model_side.include_patella == 1:
        models = [ll_model_side.pelvis_model, ll_model_side.femur_model, ll_model_side.tibfib_model,
                  ll_model_side.patella_model]
        names = ['pelvis', 'femur', 'tibfib', 'patella']
    else:
        models = [ll_model_side.pelvis_model, ll_model_side.femur_model, ll_model_side.tibfib_model]
        names = ['pelvis', 'femur', 'tibfib']
    y = 0
    for model in models:
        i_vec = np.zeros((100, 3))
        j_vec = np.zeros((100, 3))
        k_vec = np.zeros((100, 3))

        for i in range(0, 100):
            i_vec[i, :] = model.acs.o + (i * 1 * model.acs.x)
            j_vec[i, :] = model.acs.o + (i * 1 * model.acs.y)
            k_vec[i, :] = model.acs.o + (i * 1 * model.acs.z)

        v.addData('I {} {}'.format(names[y], ll_model_side.side), i_vec, render_args={'mode': 'sphere',
                                                                                      'scale_factor': 1.0,
                                                                                      'color': (1, 0, 0)})
        v.addData('J {} {}'.format(names[y], ll_model_side.side), j_vec, render_args={'mode': 'sphere',
                                                                                      'scale_factor': 1.0,
                                                                                      'color': (0, 1, 0)})
        v.addData('K {} {}'.format(names[y], ll_model_side.side), k_vec, render_args={'mode': 'sphere',
                                                                                      'scale_factor': 1.0,
                                                                                      'color': (0, 0, 1)})
        y += 1
    v.configure_traits()


def plot_all_bones_two_sides(ll_model):
    if ll_model.side == 'left' or ll_model.side == 'right':
        if ll_model.side == 'left':
            ll_model_side = ll_model.ll_l
            ll_model_side_list = [ll_model.ll_l]
        else:
            ll_model_side = ll_model.ll_r
            ll_model_side_list = [ll_model.ll_r]

        if ll_model_side.include_patella == 1:
            node_coords = np.vstack((ll_model_side.femur_model.node_coords, ll_model_side.tibfib_model.node_coords,
                                     ll_model_side.pelvis_model.node_coords, ll_model_side.patella_model.node_coords))
        else:
            node_coords = np.vstack((ll_model_side.femur_model.node_coords, ll_model_side.tibfib_model.node_coords,
                                     ll_model_side.pelvis_model.node_coords))

    elif ll_model.side == 'both':
        ll_model_side_list = [ll_model.ll_l, ll_model.ll_r]

        if ll_model.ll_l.include_patella == 1:
            node_coords = np.vstack((ll_model.ll_l.femur_model.node_coords, ll_model.ll_l.tibfib_model.node_coords,
                                     ll_model.ll_l.patella_model.node_coords, ll_model.ll_r.femur_model.node_coords,
                                     ll_model.ll_r.tibfib_model.node_coords, ll_model.ll_r.patella_model.node_coords,
                                     ll_model.ll_r.pelvis_model.node_coords))
        else:
            node_coords = np.vstack((ll_model.ll_l.femur_model.node_coords, ll_model.ll_l.tibfib_model.node_coords,
                                     ll_model.ll_r.femur_model.node_coords, ll_model.ll_r.tibfib_model.node_coords,
                                     ll_model.ll_r.pelvis_model.node_coords))

    v = fieldvi.FieldVi()
    bone_meshes = ll_model.ssm_handler.obtain_mesh_from_point_cloud(node_coords)
    v.addTri('bone_meshes', bone_meshes, render_args={'mode': 'sphere', 'scale_factor': 1.0, 'color': (1, 1, 1)})

    for ll_model_side in ll_model_side_list:
        if ll_model_side.include_patella == 1:
            models = [ll_model_side.pelvis_model, ll_model_side.femur_model, ll_model_side.tibfib_model,
                      ll_model_side.patella_model]
            names = ['pelvis', 'femur', 'tibfib', 'patella']
        else:
            models = [ll_model_side.pelvis_model, ll_model_side.femur_model, ll_model_side.tibfib_model]
            names = ['pelvis', 'femur', 'tibfib', 'patella']

        y = 0
        for model in models:
            i_vec = np.zeros((100, 3))
            j_vec = np.zeros((100, 3))
            k_vec = np.zeros((100, 3))

            for i in range(0, 100):
                i_vec[i, :] = model.acs.o + (i * 1 * model.acs.x)
                j_vec[i, :] = model.acs.o + (i * 1 * model.acs.y)
                k_vec[i, :] = model.acs.o + (i * 1 * model.acs.z)

            v.addData('I {} {}'.format(names[y], ll_model_side.side), i_vec, render_args={'mode': 'sphere',
                                                                                          'scale_factor': 1.0,
                                                                                          'color': (1, 0, 0)})
            v.addData('J {} {}'.format(names[y], ll_model_side.side), j_vec, render_args={'mode': 'sphere',
                                                                                          'scale_factor': 1.0,
                                                                                          'color': (0, 1, 0)})
            v.addData('K {} {}'.format(names[y], ll_model_side.side), k_vec, render_args={'mode': 'sphere',
                                                                                          'scale_factor': 1.0,
                                                                                          'color': (0, 0, 1)})
            y += 1
    v.configure_traits()


def plot_all_bones_with_segmentations(ll_model, segmentations):
    if ll_model.side == 'left' or ll_model.side == 'right':
        if ll_model.side == 'left':
            ll_model_side = ll_model.ll_l
            ll_model_side_list = [ll_model.ll_l]
        else:
            ll_model_side = ll_model.ll_r
            ll_model_side_list = [ll_model.ll_r]

        if ll_model_side.include_patella == 1:
            node_coords = np.vstack((ll_model_side.femur_model.node_coords, ll_model_side.tibfib_model.node_coords,
                                     ll_model_side.pelvis_model.node_coords, ll_model_side.patella_model.node_coords))
        else:
            node_coords = np.vstack((ll_model_side.femur_model.node_coords, ll_model_side.tibfib_model.node_coords,
                                     ll_model_side.pelvis_model.node_coords))

    elif ll_model.side == 'both':
        ll_model_side_list = [ll_model.ll_l, ll_model.ll_r]

        if ll_model.ll_l.include_patella == 1:
            node_coords = np.vstack((ll_model.ll_l.femur_model.node_coords, ll_model.ll_l.tibfib_model.node_coords,
                                     ll_model.ll_l.patella_model.node_coords, ll_model.ll_r.femur_model.node_coords,
                                     ll_model.ll_r.tibfib_model.node_coords, ll_model.ll_r.patella_model.node_coords,
                                     ll_model.ll_r.pelvis_model.node_coords))
        else:
            node_coords = np.vstack((ll_model.ll_l.femur_model.node_coords, ll_model.ll_l.tibfib_model.node_coords,
                                     ll_model.ll_r.femur_model.node_coords, ll_model.ll_r.tibfib_model.node_coords,
                                     ll_model.ll_r.pelvis_model.node_coords))

    v = fieldvi.FieldVi()
    bone_meshes = ll_model.ssm_handler.obtain_mesh_from_point_cloud(node_coords)
    v.addTri('bone_meshes', bone_meshes, render_args={'mode': 'sphere', 'scale_factor': 1.0, 'color': (1, 1, 1)})

    for ll_model_side in ll_model_side_list:
        if ll_model_side.include_patella == 1:
            models = [ll_model_side.pelvis_model, ll_model_side.femur_model, ll_model_side.tibfib_model,
                      ll_model_side.patella_model]
        else:
            models = [ll_model_side.pelvis_model, ll_model_side.femur_model, ll_model_side.tibfib_model]

        for model in models:
            i_vec = np.zeros((100, 3))
            j_vec = np.zeros((100, 3))
            k_vec = np.zeros((100, 3))

            for i in range(0, 100):
                i_vec[i, :] = model.acs.o + (i * 1 * model.acs.x)
                j_vec[i, :] = model.acs.o + (i * 1 * model.acs.y)
                k_vec[i, :] = model.acs.o + (i * 1 * model.acs.z)

            v.addData('I {} {}'.format(model.name, ll_model_side.side), i_vec, render_args={'mode': 'sphere',
                                                                                            'scale_factor': 1.0,
                                                                                            'color': (1, 0, 0)})
            v.addData('J {} {}'.format(model.name, ll_model_side.side), j_vec, render_args={'mode': 'sphere',
                                                                                            'scale_factor': 1.0,
                                                                                            'color': (0, 1, 0)})
            v.addData('K {} {}'.format(model.name, ll_model_side.side), k_vec, render_args={'mode': 'sphere',
                                                                                            'scale_factor': 1.0,
                                                                                            'color': (0, 0, 1)})
    segmentation_vertices = []
    for key in segmentations.keys():
        segmentation_vertices.append(segmentations[key].v)
    segmentation_vertices = np.vstack(segmentation_vertices)

    v.addData('segmentation_vertices', segmentation_vertices, render_args={'mode': 'sphere',
                                                                           'scale_factor': 1.0,
                                                                           'color': (1, 0, 1)})
    v.configure_traits()


def plot_all_bones_with_source_and_target_lms(ll_model, source_lms, target_lms, side):

    if side == 'left':
        if ll_model.include_patella == 1:
            node_coords = np.vstack((ll_model.ll_l.pelvis_model.node_coords, ll_model.ll_l.femur_model.node_coords,
                                     ll_model.ll_l.tibfib_model.node_coords,
                                     ll_model.ll_l.patella_model.node_coords))
        else:
            node_coords = np.vstack((ll_model.ll_l.pelvis_model.node_coords, ll_model.ll_l.femur_model.node_coords,
                                     ll_model.ll_l.tibfib_model.node_coords
                                     ))

        v = fieldvi.FieldVi()

        bone_meshes = ll_model.ll_l.ssm_handler.obtain_mesh_from_point_cloud(node_coords)
        v.addTri('bone_meshes', bone_meshes, render_args={'mode': 'sphere', 'scale_factor': 1.0, 'color': (1, 1, 1)})

    elif side == 'right':
        if ll_model.include_patella == 1:
            node_coords = np.vstack((ll_model.ll_r.pelvis_model.node_coords,ll_model.ll_r.femur_model.node_coords, ll_model.ll_r.tibfib_model.node_coords,
                                      ll_model.ll_r.patella_model.node_coords))
        else:
            node_coords = np.vstack((ll_model.ll_r.pelvis_model.node_coords, ll_model.ll_r.femur_model.node_coords, ll_model.ll_r.tibfib_model.node_coords,
                                     ))

        v = fieldvi.FieldVi()

        bone_meshes = ll_model.ll_r.ssm_handler.obtain_mesh_from_point_cloud(node_coords)
        v.addTri('bone_meshes', bone_meshes, render_args={'mode': 'sphere', 'scale_factor': 1.0, 'color': (1, 1, 1)})

    if side == 'left':
        models = [ll_model.ll_l.pelvis_model, ll_model.ll_l.femur_model, ll_model.ll_l.tibfib_model]
    elif side == 'right':
        models = [ll_model.ll_r.pelvis_model, ll_model.ll_r.femur_model, ll_model.ll_r.tibfib_model]
    #else:
    #    models = [ll_model.ll.pelvis_model_l, ll_model.ll.femur_model_l, ll_model.ll.tibfib_model_l,
    #              ll_model.ll.pelvis_model_r, ll_model.ll.femur_model_r, ll_model.ll.tibfib_model_r]

    for model in models:
        i_vec = np.zeros((100, 3))
        j_vec = np.zeros((100, 3))
        k_vec = np.zeros((100, 3))

        for i in range(0, 100):
            i_vec[i, :] = model.acs.o + (i * 1 * model.acs.x)
            j_vec[i, :] = model.acs.o + (i * 1 * model.acs.y)
            k_vec[i, :] = model.acs.o + (i * 1 * model.acs.z)

        v.addData('I {} {}'.format(model.name, ll_model.side), i_vec, render_args={'mode': 'sphere',
                                                                                        'scale_factor': 5.0,
                                                                                        'color': (1, 0, 0)})

        v.addData('J {} {}'.format(model.name, ll_model.side), j_vec, render_args={'mode': 'sphere',
                                                                                        'scale_factor': 5.0,
                                                                                        'color': (0, 1, 0)})
        v.addData('K {} {}'.format(model.name, ll_model.side), k_vec, render_args={'mode': 'sphere',
                                                                                        'scale_factor': 5.0,
                                                                                        'color': (0, 0, 1)})
    v.addData('source landmarks', np.asarray(source_lms), render_args={'mode': 'sphere',
                                                                       'scale_factor': 7.0,
                                                                       'color': (1, 0, 0)})
    v.addData('target landmarks', np.asarray(target_lms), render_args={'mode': 'sphere',
                                                                       'scale_factor': 7.0,
                                                                       'color': (0, 1, 0)})
    v.configure_traits()
    '''
    elif ll_model.side == 'both':
        ll_model_side_list = [ll_model.ll, ll_model.ll]
        sides = ['left','right']

        if ll_model.ll.include_patella == 1:
            node_coords_l = np.vstack((ll_model.ll.pelvis_model_l.node_coords, ll_model.ll.femur_model_l.node_coords,
                                       ll_model.ll.tibfib_model_l.node_coords, ll_model.ll.patella_model_l.node_coords))
            node_coords_r = np.vstack((ll_model.ll.pelvis_model_r.node_coords, ll_model.ll.femur_model_r.node_coords,
                                       ll_model.ll.tibfib_model_r.node_coords, ll_model.ll.patella_model_r.node_coords))
        else:
            node_coords_l = np.vstack((ll_model.ll.pelvis_model_l.node_coords, ll_model.ll.femur_model_l.node_coords,
                                       ll_model.ll.tibfib_model_l.node_coords))
            node_coords_r = np.vstack((ll_model.ll.pelvis_model_r.node_coords, ll_model.ll.femur_model_r.node_coords,
                                       ll_model.ll.tibfib_model_r.node_coords))
        v = fieldvi.FieldVi()

        bone_meshes_l = ll_model.ll.ssm_handler_l.obtain_mesh_from_point_cloud(node_coords_l)
        bone_meshes_r = ll_model.ll.ssm_handler_r.obtain_mesh_from_point_cloud(node_coords_r)
        v.addTri('bone_meshes_l', bone_meshes_l, render_args={'mode': 'sphere', 'scale_factor': 1.0, 'color': (1, 1, 1)})
        v.addTri('bone_meshes_r', bone_meshes_r, render_args={'mode': 'sphere', 'scale_factor': 1.0, 'color': (1, 1, 1)})
        '''

def plot_all_bones(ll_model):
    if ll_model.side == 'left' or ll_model.side == 'right':
        if ll_model.side == 'left':
            ll_model_side = ll_model.ll_l
            ll_model_side_list = [ll_model.ll_l]
        else:
            ll_model_side = ll_model.ll_r
            ll_model_side_list = [ll_model.ll_r]

        if ll_model_side.include_patella == 1:
            node_coords = np.vstack((ll_model_side.femur_model.node_coords, ll_model_side.tibfib_model.node_coords,
                                     ll_model_side.pelvis_model.node_coords, ll_model_side.patella_model.node_coords))
        else:
            node_coords = np.vstack((ll_model_side.femur_model.node_coords, ll_model_side.tibfib_model.node_coords,
                                     ll_model_side.pelvis_model.node_coords))

    elif ll_model.side == 'both':
        ll_model_side_list = [ll_model.ll_l, ll_model.ll_r]

        if ll_model.ll_l.include_patella == 1:
            node_coords = np.vstack((ll_model.ll_l.femur_model.node_coords, ll_model.ll_l.tibfib_model.node_coords,
                                     ll_model.ll_l.patella_model.node_coords, ll_model.ll_r.femur_model.node_coords,
                                     ll_model.ll_r.tibfib_model.node_coords, ll_model.ll_r.patella_model.node_coords,
                                     ll_model.ll_r.pelvis_model.node_coords))
        else:
            node_coords = np.vstack((ll_model.ll_l.femur_model.node_coords, ll_model.ll_l.tibfib_model.node_coords,
                                     ll_model.ll_r.femur_model.node_coords, ll_model.ll_r.tibfib_model.node_coords,
                                     ll_model.ll_r.pelvis_model.node_coords))

    v = fieldvi.FieldVi()
    bone_meshes = ll_model.ssm_handler.obtain_mesh_from_point_cloud(node_coords)
    v.addTri('bone_meshes', bone_meshes, render_args={'mode': 'sphere', 'scale_factor': 1.0, 'color': (1, 1, 1)})

    for ll_model_side in ll_model_side_list:
        if ll_model_side.include_patella == 1:
            models = [ll_model_side.pelvis_model, ll_model_side.femur_model, ll_model_side.tibfib_model,
                      ll_model_side.patella_model]
        else:
            models = [ll_model_side.pelvis_model, ll_model_side.femur_model, ll_model_side.tibfib_model]

        for model in models:
            i_vec = np.zeros((100, 3))
            j_vec = np.zeros((100, 3))
            k_vec = np.zeros((100, 3))

            for i in range(0, 100):
                i_vec[i, :] = model.acs.o + (i * 1 * model.acs.x)
                j_vec[i, :] = model.acs.o + (i * 1 * model.acs.y)
                k_vec[i, :] = model.acs.o + (i * 1 * model.acs.z)

            v.addData('I {} {}'.format(model.name, ll_model_side.side), i_vec, render_args={'mode': 'sphere',
                                                                                            'scale_factor': 1.0,
                                                                                            'color': (1, 0, 0)})
            v.addData('J {} {}'.format(model.name, ll_model_side.side), j_vec, render_args={'mode': 'sphere',
                                                                                            'scale_factor': 1.0,
                                                                                            'color': (0, 1, 0)})
            v.addData('K {} {}'.format(model.name, ll_model_side.side), k_vec, render_args={'mode': 'sphere',
                                                                                            'scale_factor': 1.0,
                                                                                            'color': (0, 0, 1)})
    v.configure_traits()


def plot_acs_per_bone_with_target_lms(origin, x, y, z, node_coords):
    target_lms_file = r'{}\target_landmarks\target_landmarks_17_3883.txt'.format(os.getcwd())
    target_landmarks_original = {}
    with open(target_lms_file) as f:
        for line in f.readlines():
            split_line = line.split(" ")
            target_landmarks_original[split_line[0]] = \
                [float(split_line[1]), float(split_line[2]), float(split_line[3][:-1])]

    target_landmarks = []
    for key in target_landmarks_original.keys():
        target_landmarks.append(target_landmarks_original[key])

    i_vec = np.zeros((100, 3))
    j_vec = np.zeros((100, 3))
    k_vec = np.zeros((100, 3))

    for i in range(0, 100):
        i_vec[i, :] = origin + (i * 1 * x)
        j_vec[i, :] = origin + (i * 1 * y)
        k_vec[i, :] = origin + (i * 1 * z)

    v = fieldvi.FieldVi()
    v.addData('nodes', node_coords, render_args={'mode': 'sphere', 'scale_factor': 1.0, 'color': (0, 1, 1)})
    v.addData('I', i_vec, render_args={'mode': 'sphere', 'scale_factor': 1.0, 'color': (1, 0, 0)})
    v.addData('J', j_vec, render_args={'mode': 'sphere', 'scale_factor': 1.0, 'color': (0, 1, 0)})
    v.addData('K', k_vec, render_args={'mode': 'sphere', 'scale_factor': 1.0, 'color': (0, 0, 1)})
    v.addData('target landmarks', np.asarray(target_landmarks), render_args={'mode': 'sphere',
                                                                             'scale_factor': 3.0,
                                                                             'color': (0, 1, 0)})
    v.configure_traits()
