import LowerLimbSide


class LowerLimb:
    def __init__(self, ssm_handler, general_fit_settings):
        self.name = general_fit_settings['name']
        self.side = general_fit_settings['side']
        self.include_patella = general_fit_settings['include_patella']
        self.ssm_handler = ssm_handler

        self.lower_limb_settings = {'dof': {'N_PARAMS_PELVIS': 6,
                                            'N_PARAMS_HIP': 3,
                                            'N_PARAMS_KNEE': 2}, 'directions': {'left': {'hip_flex_coeff': 1.0,
                                                                                         'hip_add_coeff': -1.0,
                                                                                         'hip_rot_coeff': -1.0,
                                                                                         'knee_flex_coeff': -1.0,
                                                                                         'knee_add_coeff': -1.0},
                                                                                'right': {'hip_flex_coeff': 1.0,
                                                                                          'hip_add_coeff': 1.0,
                                                                                          'hip_rot_coeff': 1.0,
                                                                                          'knee_flex_coeff': -1.0,
                                                                                          'knee_add_coeff': 1.0}}}

        if self.side == 'both':
            self.ll_l = LowerLimbSide.LowerLimbSide('left', ssm_handler, general_fit_settings, self.lower_limb_settings)
            self.ll_r = LowerLimbSide.LowerLimbSide('right',
                                                    ssm_handler,
                                                    general_fit_settings,
                                                    self.lower_limb_settings)
        if self.side == 'left':
            self.ll_l = LowerLimbSide.LowerLimbSide('left', ssm_handler, general_fit_settings, self.lower_limb_settings)
        if self.side == 'right':
            self.ll_r = LowerLimbSide.LowerLimbSide('right',
                                                    ssm_handler,
                                                    general_fit_settings,
                                                    self.lower_limb_settings)

