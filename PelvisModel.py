from gias3.musculoskeletal.bonemodels.modelcore import ACSCartesian
from gias3.common import transform3D, math, geoprimitives
import numpy as np
from gias3.musculoskeletal import model_alignment


class PelvisModel:
    def __init__(self, ssm_handler, general_fit_settings, side):
        self.name = 'Pelvis'
        self.side = side
        self.ssm_handler = ssm_handler
        self.general_fit_settings = general_fit_settings
        self.acs = ACSCartesian((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))

        self.landmark_names = dict(left=['ASIS_VERTEX',
                                         'PSIS_VERTEX',
                                         'ACETABULAR_RIM_SUPERIOR',
                                         'ACETABULAR_RIM_ANTERIOR',
                                         'ACETABULAR_RIM_POSTERIOR'],
                                   right=['ASIS_VERTEX',
                                          'PSIS_VERTEX',
                                          'ACETABULAR_RIM_SUPERIOR',
                                          'ACETABULAR_RIM_ANTERIOR',
                                          'ACETABULAR_RIM_POSTERIOR'])

        self.bone_names = dict(left='Pel', right='Pel')

        self.landmark_node_nrs = ssm_handler.ssm_lm_node_nrs_pelvis
        self.node_coords_pel_l = None
        self.node_coords_pel_r = None
        self.node_coords_sac = None
        self.node_coords = None
        self.landmark_coords = dict(left={}, right={})
        self.region_coords = dict(left={}, right={})
        self.acetabulum_origin = dict(left={}, right={})

    def update_node_coords(self):
        node_coords_per_bone = self.ssm_handler.reconstructed_nodes_per_bone
        self.node_coords = node_coords_per_bone[self.bone_names[self.side]]
        #self.node_coords_pel_l = node_coords_per_bone[self.bone_names[self.side][0]]
        #self.node_coords_pel_r = node_coords_per_bone[self.bone_names[self.side][1]]
        #self.node_coords_sac = node_coords_per_bone[self.bone_names[self.side][2]]

        #if self.general_fit_settings['side'] == 'both':
        #    self.node_coords = np.vstack((self.node_coords_pel_l, self.node_coords_pel_r, self.node_coords_sac))
        #else:
        #    if self.side == 'left':
        #        self.node_coords = np.vstack((self.node_coords_pel_l, self.node_coords_pel_r, self.node_coords_sac))
        #    else:
        #        self.node_coords = np.vstack((self.node_coords_pel_r, self.node_coords_pel_l, self.node_coords_sac))

    def update_acs(self):
        self.acs.update(*model_alignment.createPelvisACSISB(self.landmark_coords['left']['ASIS_VERTEX'],
                                                            self.landmark_coords['right']['ASIS_VERTEX'],
                                                            self.landmark_coords['left']['PSIS_VERTEX'],
                                                            self.landmark_coords['right']['PSIS_VERTEX']))

    def update_landmarks_and_regions(self):
        for landmark_name in self.landmark_names['left']:
            #self.landmark_coords['left'].update({
            #    landmark_name: self.node_coords_pel_l[self.landmark_node_nrs['left'][landmark_name]]})
            self.landmark_coords['left'].update({
                landmark_name: self.node_coords[self.landmark_node_nrs['left'][landmark_name]]})
        for landmark_name in self.landmark_names['right']:
            #self.landmark_coords['right'].update({
            #    landmark_name: self.node_coords_pel_r[self.landmark_node_nrs['right'][landmark_name]]})
            self.landmark_coords['right'].update({
                landmark_name: self.node_coords[self.landmark_node_nrs['right'][landmark_name]]})

        self.obtain_acetabulum_sphere_centre()

    def obtain_acetabulum_cup_centre(self):
        p1 = self.landmark_coords[self.side]['ACETABULAR_RIM_SUPERIOR']
        p2 = self.landmark_coords[self.side]['ACETABULAR_RIM_ANTERIOR']
        p3 = self.landmark_coords[self.side]['ACETABULAR_RIM_POSTERIOR']
        origin, radius, normal = geoprimitives.circumcentre3Points(p1, p2, p3)
        self.acetabulum_origin[self.side] = origin

    def obtain_acetabulum_sphere_centre(self):
        acetabulum_coords = []
        for node_nr in self.ssm_handler.ssm_regions_node_nrs_pelvis[self.side]['acetabulum_nodes']:
            acetabulum_coords.append(self.node_coords[node_nr, :])
        hc, r = geoprimitives.fitSphereAnalytic(np.asarray(acetabulum_coords))
        self.acetabulum_origin[self.side] = hc
