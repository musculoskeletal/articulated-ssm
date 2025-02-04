from gias3.mesh import vtktools
import numpy as np
import os
import csv


def save_mesh_and_lms(ll_model, source_lms, target_lms, lms_to_fit, output_directory, side, xopt):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    lms_to_fit_source = np.asarray([np.append(np.copy(lms_to_fit), 'hjc')])
    lms_to_fit_source = np.asarray([np.append(lms_to_fit_source, 'condyle_lat')])
    lms_to_fit_source = np.asarray([np.append(lms_to_fit_source, 'condyle_med')])

    if side == 'left':
        model = ll_model.ll_l
    elif side == 'right':
        model = ll_model.ll_r

    if model.include_patella == 1:
        node_coords_pat = model.patella_model.node_coords

    node_coords_pel = model.pelvis_model.node_coords_pel_l
    node_coords_fem = model.femur_model.node_coords
    node_coords_tib = model.tibfib_model.node_coords

    hjc = model.pelvis_model.acetabulum_origin[side]
    condyle_lat = model.tibfib_model.landmark_coords[side]['condyle_lat']
    condyle_med = model.tibfib_model.landmark_coords[side]['condyle_med']

    target_lms_save = np.copy(target_lms[:-2])
    source_lms_save = np.copy(source_lms[:-2])
    source_lms_save = np.concatenate((source_lms_save, np.asarray([hjc]), np.asarray([condyle_lat]), np.asarray([condyle_med])), axis=0)
    bone_mesh_pel, bone_mesh_fem, bone_mesh_tib = model.ssm_handler.create_mesh_each_bone(node_coords_pel, node_coords_fem, node_coords_tib)

    output_pel = os.path.join(output_directory, f'predicted_mesh_{side}_pelvis.stl')
    output_fem = os.path.join(output_directory, f'predicted_mesh_{side}_femur.stl')
    output_tib = os.path.join(output_directory, f'predicted_mesh_{side}_tibfib.stl')
    pred_lms = os.path.join(output_directory, f'predicted_lms_{side}.txt')
    orig_lms = os.path.join(output_directory, f'orignial_lms_{side}.txt')
    x_opt = os.path.join(output_directory, f'x_opt_{side}.txt')

    pred_lms_save = np.concatenate((np.transpose(lms_to_fit_source), source_lms_save), axis=1)
    with open(pred_lms, "w+") as file:
        csv.writer(file, delimiter=" ").writerows(pred_lms_save)

    lms_to_fit_targ = np.asarray([lms_to_fit])
    orig_lms_save = np.concatenate((np.transpose(lms_to_fit_targ), target_lms_save), axis=1)
    with open(orig_lms, "w+") as file:
        csv.writer(file, delimiter=" ").writerows(orig_lms_save)

    headers = ['pelvis_rigid', 'hip_rot', 'knee_rot', 'pc_weights']
    with open(x_opt, "w+") as file:
        for header, row in zip(headers, xopt):
            file.write(f"{header} " + " ".join(map(str, row)) + "\n")

    pred_mesh_pel = vtktools.Writer(filename=output_pel, v=bone_mesh_pel.v, f=bone_mesh_pel.f)
    pred_mesh_pel.write()
    pred_mesh_fem = vtktools.Writer(filename=output_fem, v=bone_mesh_fem.v, f=bone_mesh_fem.f)
    pred_mesh_fem.write()
    pred_mesh_tib = vtktools.Writer(filename=output_tib, v=bone_mesh_tib.v, f=bone_mesh_tib.f)
    pred_mesh_tib.write()


def save_mesh_and_lms_old(ll_model, source_lms, target_lms, case, pred_path, side):
    if side == 'left':
        if ll_model.ll_l.include_patella == 1:
            node_coords = np.vstack((ll_model.ll_l.pelvis_model.node_coords, ll_model.ll_l.femur_model.node_coords,
                                     ll_model.ll_l.tibfib_model.node_coords, ll_model.ll_l.patella_model.node_coords))
        else:
            node_coords = np.vstack((ll_model.ll_l.pelvis_model.node_coords,
                                     ll_model.ll_l.femur_model.node_coords,
                                     ll_model.ll_l.tibfib_model.node_coords))

        bone_meshes = ll_model.ll_l.ssm_handler.obtain_mesh_from_point_cloud(node_coords)

        output = '{}/pred_meshes/{}/{}_predicted_mesh_left.ply'.format(os.getcwd(), pred_path, case)
        pred_lms = '{}/pred_meshes/{}/{}_predicted_lms_left.txt'.format(os.getcwd(), pred_path, case)
        orig_lms = '{}/pred_meshes/{}/{}_orignial_lms_left.txt'.format(os.getcwd(), pred_path, case)
        # acetabulum = '{}/pred_meshes/acetabulum.txt'.format(os.getcwd())

        # np.savetxt(acetabulum,np.transpose(np.array(ll_model_side.pelvis_model.acetabulum_origin['left'])))
        np.savetxt(pred_lms, source_lms)
        np.savetxt(orig_lms, target_lms)
        pred_mesh = vtktools.Writer(filename=output, v=bone_meshes.v, f=bone_meshes.f)
        pred_mesh.write()

    elif side == 'right':
        if ll_model.ll_r.include_patella == 1:
            node_coords = np.vstack((ll_model.ll_r.pelvis_model.node_coords, ll_model.ll_r.femur_model.node_coords,
                                     ll_model.ll_r.tibfib_model.node_coords, ll_model.ll_r.patella_model.node_coords))
        else:
            node_coords = np.vstack((ll_model.ll_l.pelvis_model.node_coords,
                                     ll_model.ll_r.femur_model.node_coords,
                                     ll_model.ll_r.tibfib_model.node_coords))

        bone_meshes = ll_model.ll_r.ssm_handler.obtain_mesh_from_point_cloud(node_coords)

        output = '{}/pred_meshes/{}/{}_predicted_mesh_right.ply'.format(os.getcwd(), pred_path, case)
        pred_lms = '{}/pred_meshes/{}/{}_predicted_lms_right.txt'.format(os.getcwd(), pred_path, case)
        orig_lms = '{}/pred_meshes/{}/{}_orignial_lms_right.txt'.format(os.getcwd(), pred_path, case)
        # acetabulum = '{}/pred_meshes/acetabulum.txt'.format(os.getcwd())

        # np.savetxt(acetabulum,np.transpose(np.array(ll_model_side.pelvis_model.acetabulum_origin['left'])))
        np.savetxt(pred_lms, source_lms)
        np.savetxt(orig_lms, target_lms)
        pred_mesh = vtktools.Writer(filename=output, v=bone_meshes.v, f=bone_meshes.f)
        pred_mesh.write()

    '''
    elif ll_model.side == 'both':
        if ll_model.ll.include_patella == 1:
            node_coords_l = np.vstack((ll_model.ll.pelvis_model_l.node_coords, ll_model.ll.femur_model_l.node_coords,
                                       ll_model.ll.tibfib_model_l.node_coords, ll_model.ll.patella_model_l.node_coords))

            node_coords_r = np.vstack((ll_model.ll.pelvis_model_r.node_coords, ll_model.ll.femur_model_r.node_coords,
                                       ll_model.ll.tibfib_model_r.node_coords, ll_model.ll.patella_model_r.node_coords))
        else:
            node_coords_l = np.vstack((ll_model.ll.pelvis_model_l.node_coords,ll_model.ll.femur_model_l.node_coords,
                                     ll_model.ll.tibfib_model_l.node_coords))

            node_coords_r = np.vstack((ll_model.ll.pelvis_model_r.node_coords,ll_model.ll.femur_model_r.node_coords,
                                       ll_model.ll.tibfib_model_r.node_coords))

        bone_meshes_l = ll_model.ll.ssm_handler_l.obtain_mesh_from_point_cloud(node_coords_l)
        bone_meshes_r = ll_model.ll.ssm_handler_r.obtain_mesh_from_point_cloud(node_coords_r)

        output_l = '{}/pred_meshes/{}/{}_predicted_mesh_left.ply'.format(os.getcwd(), pred_path, case)
        output_r = '{}/pred_meshes/{}/{}_predicted_mesh_right.ply'.format(os.getcwd(), pred_path, case)
        pred_lms = '{}/pred_meshes/{}/{}_predicted_lms.txt'.format(os.getcwd(), pred_path, case)
        orig_lms = '{}/pred_meshes/{}/{}_orignial_lms.txt'.format(os.getcwd(), pred_path, case)
        #acetabulum = '{}/pred_meshes/acetabulum.txt'.format(os.getcwd())

        #np.savetxt(acetabulum,np.transpose(np.array(ll_model_side.pelvis_model.acetabulum_origin['left'])))
        np.savetxt(pred_lms,source_lms)
        np.savetxt(orig_lms, target_lms)
        pred_mesh_l = vtktools.Writer(filename=output_l, v = bone_meshes_l.v, f=bone_meshes_l.f)
        pred_mesh_l.write()
        pred_mesh_r = vtktools.Writer(filename=output_r, v=bone_meshes_r.v, f=bone_meshes_r.f)
        pred_mesh_r.write()
    '''
