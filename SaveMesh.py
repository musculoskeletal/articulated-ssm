from gias3.mesh import simplemesh, vtktools
import numpy as np
import os
import open3d as o3d

def save_mesh_and_lms(ll_model, source_lms, target_lms, case, pred_path):
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
            node_coords = np.vstack((ll_model_side.pelvis_model.node_coords, ll_model_side.femur_model.node_coords,
                                     ll_model_side.tibfib_model.node_coords))


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

    bone_meshes = ll_model.ssm_handler.obtain_mesh_from_point_cloud(node_coords)

    output = '{}/pred_meshes/{}/{}_predicted_mesh.ply'.format(os.getcwd(), pred_path, case)
    pred_lms = '{}/pred_meshes/{}/{}_predicted_lms.txt'.format(os.getcwd(), pred_path, case)
    orig_lms = '{}/pred_meshes/{}/{}_orignial_lms.txt'.format(os.getcwd(), pred_path, case)
    #acetabulum = '{}/pred_meshes/acetabulum.txt'.format(os.getcwd())

    #np.savetxt(acetabulum,np.transpose(np.array(ll_model_side.pelvis_model.acetabulum_origin['left'])))
    np.savetxt(pred_lms,source_lms)
    np.savetxt(orig_lms, target_lms)
    pred_mesh = vtktools.Writer(filename=output, v = bone_meshes.v, f=bone_meshes.f)
    pred_mesh.write()
    #pred_mesh.renderPolyData()

    #mean_path = ll_model.ssm_handler.ssm_mean_file
    #mean_mesh = o3d.io.read_triangle_mesh(mean_path)
    #pred_mesh = o3d.geometry.TriangleMesh()
    #pred_mesh.vertices = o3d.utility.Vector3dVector(bone_meshes.v)
    #pred_mesh.triangles = o3d.utility.Vector3iVector(mean_mesh.triangles)
    #o3d.io.write_triangle_mesh(output, pred_mesh, write_ascii=True)