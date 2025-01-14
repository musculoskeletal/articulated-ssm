from PelvisModel import PelvisModel as PelvisModel
from FemurModel import FemurModel as FemurModel
from TibiaFibulaModel import TibiaFibulaModel as TibiaFibulaModel
from PatellaModel import PatellaModel as PatellaModel
from gias3.common import transform3D, math
import numpy as np
from scipy.spatial import cKDTree


class LowerLimbBothSide:
    def __init__(self, side, ssm_handler_l, ssm_handler_r, general_fit_settings, ll_settings):
        self.side = side
        self.ssm_handler_l = ssm_handler_l
        self.ssm_handler_r = ssm_handler_r
        self.include_patella = general_fit_settings['include_patella']
        self.N_PARAMS_PELVIS = ll_settings['dof']['N_PARAMS_PELVIS']
        self.N_PARAMS_HIP = ll_settings['dof']['N_PARAMS_HIP']
        self.N_PARAMS_KNEE = ll_settings['dof']['N_PARAMS_KNEE']
        self.N_PARAMS_RIGID = self.N_PARAMS_PELVIS + self.N_PARAMS_HIP + self.N_PARAMS_KNEE
        self._neutral_params = [[0, ],  # pc_weights_l
                                [0, ],  # pc_weights_r
                                [0, ],  # pc_modes
                                [0] * self.N_PARAMS_PELVIS,  # pelvis_rigid dof
                                [0] * self.N_PARAMS_PELVIS,  # pelvis_rigid dof
                                [0] * self.N_PARAMS_HIP,  # hip_rot dof_l
                                [0] * self.N_PARAMS_KNEE,  # knee_rot_l
                                [0] * self.N_PARAMS_HIP,  # hip_rot dof_r
                                [0] * self.N_PARAMS_KNEE]  # knee_rot_r

        self.pelvis_model_l = PelvisModel(ssm_handler_l, general_fit_settings, 'left')
        self.femur_model_l = FemurModel(ssm_handler_l, general_fit_settings, 'left')
        self.tibfib_model_l = TibiaFibulaModel(ssm_handler_l, general_fit_settings, 'left')
        if self.include_patella:
            self.patella_model_l = PatellaModel(ssm_handler_l, general_fit_settings, 'left')
        self.pelvis_model_r = PelvisModel(ssm_handler_r, general_fit_settings, 'right')
        self.femur_model_r = FemurModel(ssm_handler_r, general_fit_settings, 'right')
        self.tibfib_model_r = TibiaFibulaModel(ssm_handler_r, general_fit_settings, 'right')
        if self.include_patella:
            self.patella_model_r = PatellaModel(ssm_handler_r, general_fit_settings, 'right')

        self.direction_parameters = ll_settings['directions']
        self.knee_gap = general_fit_settings['knee_gap']
        self.knee_fixed = general_fit_settings['knee_fixed']
        self.allow_knee_adduction_dof = general_fit_settings['allow_knee_adduction_dof']
        self.allow_knee_adduction_correction = general_fit_settings['allow_knee_adduction_correction']
        self.loo = general_fit_settings['LOO']

    def load_bones_and_model(self):
        # Load bone models and set to neutral positions
        # zero shape model

        # left side
        self.ssm_handler_l.load_coupled_ssm()
        self.ssm_handler_l.reconstruct_ssm([0, ], [0, ])
        self.ssm_handler_l.split_ssm_geometry_per_bone(self.ssm_handler_l.reconstructed)

        #self.ssm_handler_l.split_ssm_geometry_per_bone(self.ssm_handler_l.ssm_mean.v)
        self.femur_model_l.update_node_coords()
        self.femur_model_l.update_landmarks_and_regions()
        self.femur_model_l.update_acs()
        self.tibfib_model_l.update_node_coords()
        self.tibfib_model_l.update_landmarks_and_regions()
        self.tibfib_model_l.update_acs()
        self.pelvis_model_l.update_node_coords()
        self.pelvis_model_l.update_landmarks_and_regions()
        if self.include_patella:
            self.patella_model_l.update_node_coords()
            self.patella_model_l.update_landmarks_and_regions()
            self.patella_model_l.update_acs()

        # right side
        self.ssm_handler_r.load_coupled_ssm()
        self.ssm_handler_r.reconstruct_ssm([0, ], [0, ])
        self.ssm_handler_r.split_ssm_geometry_per_bone(self.ssm_handler_r.reconstructed)
        #self.ssm_handler_r.split_ssm_geometry_per_bone(self.ssm_handler_r.ssm_mean.v)
        self.femur_model_r.update_node_coords()
        self.femur_model_r.update_landmarks_and_regions()
        self.femur_model_r.update_acs()
        self.tibfib_model_r.update_node_coords()
        self.tibfib_model_r.update_landmarks_and_regions()
        self.tibfib_model_r.update_acs()
        self.pelvis_model_r.update_node_coords()
        self.pelvis_model_r.update_landmarks_and_regions()

        # keep pelvis CS consistent
        self.pelvis_model_l.update_acs()
        self.pelvis_model_r.update_acs()

        if self.include_patella:
            self.patella_model_r.update_node_coords()
            self.patella_model_r.update_landmarks_and_regions()
            self.patella_model_r.update_acs()

        # zero model again, this time with angles and hip and knee set
        self.update_all_models(*self._neutral_params)

    def update_all_models(self, pc_weights_l, pc_weights_r, pc_modes, pelvis_rigid_l, pelvis_rigid_r, hip_rot_l, knee_rot_l, hip_rot_r,
                          knee_rot_r):
        """Update the lower limb geometry by pc weights and rigid transformations
        Inputs:
        pc_weights [list of floats]: list of pc weights for right and left side shape modesl
        pc_modes [list of ints]: list of the pcs that the weights are for
        pelvis_rigid [1-d array]: an array of six elements defining the rigid body
            translation and rotation for the pelvis.
        hip_rot [1-d array]: an array of 3 radian angles for femur rotation about the
            hip joint (flexion, rotation, adduction) for left and right side
        knee_rot [1-d array]: an array of radian angles for tibia-fibula rotation
            about the knee joint (flexion) for left and right side
        """
        # evaluate shape model
        self.update_models_by_pcweights_sd(pc_weights_l, pc_weights_r, pc_modes)

        # rigid transform pelvis
        self.update_pelvis(pelvis_rigid_l, 'left')
        self.update_pelvis(pelvis_rigid_r, 'right')

        # place femur by hip rotation
        self.update_femur(hip_rot_l, 'left')
        self.update_femur(hip_rot_r, 'right')

        # place tibia and fibula by knee_rot and default_knee_offset
        self.update_tibiafibula(knee_rot_l, 'left')
        self.update_tibiafibula(knee_rot_r, 'right')

        # place patella relative to tibia
        if self.include_patella == 1:
            self.update_patella('left')
            self.update_patella('right')

        # self.put_all_landmark_coords_in_one_dict()

    def update_models_by_pcweights_sd(self, pc_weights_l, pc_weights_r, pc_modes):
        # left side

        self.ssm_handler_l.reconstruct_ssm(pc_weights_l, pc_modes)
        self.ssm_handler_l.split_ssm_geometry_per_bone(self.ssm_handler_l.reconstructed)

        self.femur_model_l.update_node_coords()
        self.femur_model_l.update_landmarks_and_regions()
        self.femur_model_l.update_acs()

        self.pelvis_model_l.update_node_coords()
        self.pelvis_model_l.update_landmarks_and_regions()

        self.tibfib_model_l.update_node_coords()
        self.tibfib_model_l.update_landmarks_and_regions()
        self.tibfib_model_l.update_acs()

        if self.include_patella:
            self.patella_model_l.update_node_coords()
            self.patella_model_l.update_landmarks_and_regions()
            self.patella_model_l.update_acs()

        # right side
        self.ssm_handler_r.reconstruct_ssm(pc_weights_r, pc_modes)
        self.ssm_handler_r.split_ssm_geometry_per_bone(self.ssm_handler_r.reconstructed)

        self.femur_model_r.update_node_coords()
        self.femur_model_r.update_landmarks_and_regions()
        self.femur_model_r.update_acs()

        self.pelvis_model_r.update_node_coords()
        self.pelvis_model_r.update_landmarks_and_regions()

        self.tibfib_model_r.update_node_coords()
        self.tibfib_model_r.update_landmarks_and_regions()
        self.tibfib_model_r.update_acs()

        if self.include_patella:
            self.patella_model_r.update_node_coords()
            self.patella_model_r.update_landmarks_and_regions()
            self.patella_model_r.update_acs()

        self.pelvis_model_l.update_acs()
        self.pelvis_model_r.update_acs()

    def update_pelvis(self, pelvis_rigid, side):
        """Update position and orientation of the pelvis.
        Inputs:
        pelvis_rigid [list]: list of 6 floats describing a rigid transformation in the global coordinate system of the
            pelvis - [tx, ty, tz, rx, ry, rz]. Rotation is about the origin of the pelvis anatomic coordinate system.
        """

        if side == 'left':
            pel = self.pelvis_model_l
        elif side == 'right':
            pel = self.pelvis_model_r

        _pel_origin = pel.acs.o

        pel.node_coords_pel_l = transform3D.transformRigid3DAboutP(pel.node_coords_pel_l, pelvis_rigid, _pel_origin)
        pel.node_coords_pel_r = transform3D.transformRigid3DAboutP(pel.node_coords_pel_r, pelvis_rigid, _pel_origin)
        pel.node_coords = np.vstack((pel.node_coords_pel_l, pel.node_coords_pel_r))

        pel.update_landmarks_and_regions()

        pel.update_acs()

    def update_femur(self, hip_rot, side):
        """Update position and orientation of the femur segment.
        inputs:
        hip_rot [list]: list of 3 floats describing hip flexion, rotation, and adduction in radians.
        """
        if side == 'left':
            fem = self.femur_model_l
        elif side == 'right':
            fem = self.femur_model_r

        # align femur to neutral hip CS
        self.reset_femur_hip(side)

        # get joint cs
        o, flex, rot, abd = self.get_hip_acs(side)

        # apply hip rotations:
        # flexion (pelvis-z)
        fem.node_coords = transform3D.transformRotateAboutAxis(fem.node_coords,
                                                               self.direction_parameters[side]
                                                               ['hip_flex_coeff'] * hip_rot[0],
                                                               o,
                                                               o + flex)

        fem.update_landmarks_and_regions()
        fem.update_acs()

        # abduction (floating)
        fem.node_coords = transform3D.transformRotateAboutAxis(fem.node_coords,
                                                               self.direction_parameters[side]
                                                               ['hip_add_coeff'] * hip_rot[2],
                                                               o,
                                                               o + abd)

        fem.update_landmarks_and_regions()
        fem.update_acs()

        # rotations (femur-z)

        fem.node_coords = transform3D.transformRotateAboutAxis(fem.node_coords,
                                                               self.direction_parameters[side]
                                                               ['hip_rot_coeff'] * hip_rot[1],
                                                               o,
                                                               o + rot)

        fem.update_landmarks_and_regions()
        fem.update_acs()

    def reset_femur_hip(self, side):
        """Reset femur position to have 0 rotations at the hip.
        i.e. align femur ACS with pelvis ACS at the HJC
        """
        if side == 'left':
            fem = self.femur_model_l
            pel = self.pelvis_model_l
        elif side == 'right':
            fem = self.femur_model_r
            pel = self.pelvis_model_r

        # translate axes to femur system
        op = pel.acetabulum_origin[side]
        cs_targ = np.array([op,
                            op + pel.acs.x,
                            op + pel.acs.y,
                            op + pel.acs.z])

        of = fem.femoral_head_centre
        cs_source = np.array([of,
                              of + fem.acs.x,
                              of + fem.acs.y,
                              of + fem.acs.z])
        t = transform3D.directAffine(cs_source, cs_targ)

        fem.node_coords = transform3D.transformAffine(fem.node_coords, t)
        fem.update_landmarks_and_regions()
        fem.update_acs()

    def get_hip_acs(self, side):
        if side == 'left':
            fem = self.femur_model_l
            pel = self.pelvis_model_l
        elif side == 'right':
            fem = self.femur_model_r
            pel = self.pelvis_model_r

        o = pel.acetabulum_origin[side]
        abd = math.norm(np.cross(fem.acs.y, pel.acs.z))  # floating axis
        rot = fem.acs.y  # rotation
        flex = pel.acs.z  # flexion
        return np.array([o, flex, rot, abd])

    def update_tibiafibula(self, knee_rot, side):
        """Update position and orientation of the tibiafibula segment.
        inputs:
        knee_rot [list of floats]: knee flexion and adduction angle in radians.
        """
        if side == 'left':
            tib = self.tibfib_model_l
        elif side == 'right':
            tib = self.tibfib_model_r

        # align tibia to neutral knee CS
        self.reset_tibia_knee(side)

        if not self.knee_fixed:
            # get joint cs
            o, flex, rot, abd = self.get_knee_acs(side)

            # apply knee rotations: flexion(femur-z)
            tib.node_coords = transform3D.transformRotateAboutAxis(tib.node_coords,
                                                                   self.direction_parameters[side]
                                                                   ['knee_flex_coeff'] * knee_rot[0],
                                                                   o,
                                                                   o + flex)
            tib.update_landmarks_and_regions()
            tib.update_acs()

            # apply knee rotation: adduction(floating x)
            if self.allow_knee_adduction_dof:
                tib.node_coords = transform3D.transformRotateAboutAxis(tib.node_coords,
                                                                       self.direction_parameters[side]
                                                                       ['knee_add_coeff'] * knee_rot[1],
                                                                       o,
                                                                       o + abd)
                tib.update_landmarks_and_regions()
                tib.update_acs()

            # reset knee gap
            if self.allow_knee_adduction_correction:
                self.reset_tibia_kneegap_2(side)
            else:
                self.reset_tibia_kneegap_1(side)

    def reset_tibia_knee(self, side):
        """Reset tibia position to have 0 rotations at the knee.
        i.e. align tibia ACS with femur ACS at the femur origin
        """
        if side == 'left':
            fem = self.femur_model_l
            tib = self.tibfib_model_l
        elif side == 'right':
            fem = self.femur_model_r
            tib = self.tibfib_model_r
        # translate axes to femur system
        of = fem.acs.o
        cs_targ = np.array([of,
                            of + fem.acs.x,
                            of + fem.acs.y,
                            of + fem.acs.z,
                            ])

        ot = 0.5 * (tib.landmark_coords[side]['condyle_med'] +
                    tib.landmark_coords[side]['condyle_lat'])

        cs_source = np.array([ot,
                              ot + tib.acs.x,
                              ot + tib.acs.y,
                              ot + tib.acs.z,
                              ])

        t = transform3D.directAffine(cs_source, cs_targ)

        tib.node_coords = transform3D.transformAffine(tib.node_coords, t)
        tib.update_landmarks_and_regions()
        tib.update_acs()

        self.reset_tibia_kneegap_1(side)

    def reset_tibia_kneegap_1(self, side):
        """shift tibia along tibia y to maintain knee joint gap
        """
        if side == 'left':
            tib = self.tibfib_model_l
        elif side == 'right':
            tib = self.tibfib_model_r
        # self.femur_model.get_knee_surface_pts(self)
        # self.tibfib_model.get_knee_surface_pts(self)
        current_knee_gap = self.calc_knee_gap(side)
        knee_shift = current_knee_gap - self.knee_gap
        shift_t = knee_shift * tib.acs.y
        tib.node_coords = tib.node_coords + shift_t
        tib.update_landmarks_and_regions()
        tib.update_acs()

    def reset_tibia_kneegap_2(self, side):
        """shift and reorient tibia to fit to femoral condyles. Allow rotation
        in its x-axis
        """
        if side == 'left':
            tib = self.tibfib_model_l
            fem = self.femur_model_l
        elif side == 'right':
            tib = self.tibfib_model_r
            fem = self.femur_model_r
        # place tibia as per normal
        self.reset_tibia_kneegap_1(side)

        # build ckdtree of femoral condyle points
        femur_tree = cKDTree(np.asarray(fem.region_coords[side]['knee_nodes']))

        # calculate and apply varus-valgus angle (about floating-x)
        varus_angle = self.calc_varus_angle(femur_tree,side)[0]

        floating_x = math.norm(np.cross(tib.acs.y, fem.acs.z))
        tib.node_coords = transform3D.transformRotateAboutAxis(tib.node_coords,
                                                               -varus_angle,
                                                               fem.acs.o,
                                                               fem.acs.o + floating_x)

        tib.update_landmarks_and_regions()
        tib.update_acs()

    def calc_knee_gap(self, side):
        """Calculate the closest distance between points on the femoral
        knee articular surface and the tibial knee articular surface.
        """
        if side == 'left':
            tib = self.tibfib_model_l
            fem = self.femur_model_l
        elif side == 'right':
            tib = self.tibfib_model_r
            fem = self.femur_model_r
        # evaluate points
        femur_points = np.asarray(fem.region_coords[side]['knee_nodes'])
        tibia_points = np.asarray(tib.region_coords[side]['knee_nodes'])

        # find closest neighbours
        femur_tree = cKDTree(femur_points)
        dist, femur_points_i = femur_tree.query(tibia_points)

        # calc distance in the tibial Y for each pair
        tibia_y_dist = np.dot(femur_points[femur_points_i] - tibia_points, tib.acs.y)

        return tibia_y_dist.min()

    def get_knee_acs(self, side):
        """Returns knee joint coordinate system:
        [origin, flexion axis, rotation axis, abduction axis]
        """
        if side == 'left':
            tib = self.tibfib_model_l
            fem = self.femur_model_l
        elif side == 'right':
            tib = self.tibfib_model_r
            fem = self.femur_model_r
        o = fem.acs.o  # origin
        abd = math.norm(np.cross(tib.acs.y, fem.acs.z))  # abduction, floating axis
        rot = tib.acs.y  # rotation
        flex = fem.acs.z  # flexion
        return np.array([o, flex, rot, abd])

    def calc_varus_angle(self, femur_points_tree, side):

        if side == 'left':
            tib = self.tibfib_model_l
            fem = self.femur_model_l
        elif side == 'right':
            tib = self.tibfib_model_r
            fem = self.femur_model_r
        # evaluate tibial plateau points
        tp_lat = tib.landmark_coords[side]['tib_plateau_lat']
        tp_med = tib.landmark_coords[side]['tib_plateau_med']

        # tibial plateau vector
        if side == 'left':
            tp_v = tp_med - tp_lat
        else:
            tp_v = tp_lat - tp_med
        # find the closest femur condyle points to tp_lat and tp_med
        (med_d, lat_d), (fc_med_i, fc_lat_i) = femur_points_tree.query([tp_med, tp_lat])

        if fc_med_i == fc_lat_i:  # To make sure fc_v is not NaN
            fc_med_i -= 1

        # femoral condyle vector
        if side == 'left':
            fc_v = femur_points_tree.data[fc_med_i] - femur_points_tree.data[fc_lat_i]
        else:
            fc_v = femur_points_tree.data[fc_lat_i] - femur_points_tree.data[fc_med_i]
        # project vectors to Z-Y plane
        z = fem.acs.z
        y = fem.acs.y
        tp_v_zy = np.array([np.dot(tp_v, z), np.dot(tp_v, y)])
        fc_v_zy = np.array([np.dot(fc_v, z), np.dot(fc_v, y)])

        # calc angle in Z-Y plane
        tp_fc_angle = abs(math.angle(tp_v_zy, fc_v_zy))

        # if lat condyle is higher than med condyle, negative rotation is needed
        if side == 'left':
            if lat_d > med_d:
                tp_fc_angle *= -1.0
        else:
            if med_d > lat_d:
                tp_fc_angle *= -1.0

        return tp_fc_angle, (lat_d, med_d)

    def update_patella(self, side):
        """Update patella position and orientation. Patella is placed a fixed distance
        from the tibia in the tibial Y direction"""

        if side == 'left':
            tib = self.tibfib_model_l
            pat = self.patella_model_l
        else:
            tib = self.tibfib_model_r
            pat = self.patella_model_r
        # align patella acs to tibial acs, centred at midpoint of tibial epicondyles
        ot = 0.5 * (tib.landmark_coords[self.side]['condyle_lat'] +
                    tib.landmark_coords[self.side]['condyle_med'])

        cs_targ = np.array([ot,
                            ot + tib.acs.x,
                            ot + tib.acs.y,
                            ot + tib.acs.z,
                            ])

        cs_source = pat.acs.unit_array

        t1 = transform3D.directAffine(cs_source, cs_targ)
        pat.node_coords = transform3D.transformAffine(x=pat.node_coords, t=t1)
        pat.update_landmarks_and_regions()
        pat.update_acs()

        # apply patella shift
        t2 = tib.acs.x * pat.patella_shift[0] + \
             tib.acs.y * pat.patella_shift[1] + \
             tib.acs.z * pat.patella_shift[2]

        pat.node_coords = pat.node_coords + t2
        pat.update_landmarks_and_regions()
        pat.update_acs()
