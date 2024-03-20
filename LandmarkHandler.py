import numpy as np
import correct_markers as cm

class LandmarkHandler:
    def __init__(self, target_lms_file, landmark_names_to_fit, ll_model, correct_markers, side):
        self.landmark_names_to_fit = landmark_names_to_fit
        self.ll_model = ll_model
        self.side = ll_model.side
        self.target_landmarks_original = {}
        self.target_landmarks = dict(left={}, right={}, sacrum={})
        self.source_landmarks = dict(left={}, right={}, sacrum={})
        self.update_source_landmarks_dict()
        self.load_target_landmarks_from_txt(target_lms_file)
        self.create_target_landmarks_dict()
        if correct_markers:
            cm.correct_target_markers(self.target_landmarks,side)

    def load_target_landmarks_from_txt(self, target_lms_file):
        with open(target_lms_file) as f:
            for line in f.readlines():
                split_line = line.split(" ")
                self.target_landmarks_original[split_line[0]] = \
                    [float(split_line[1]), float(split_line[2]), float(split_line[3][:-1])]

    def create_target_landmarks_dict(self):
        sides = ['left', 'right']
        for landmark_name in self.landmark_names_to_fit:
            for key in self.target_landmarks_original.keys():
                if landmark_name in key:
                    for side in sides:
                        if side in key:
                            self.target_landmarks[side].update({landmark_name: self.target_landmarks_original[key]})

        psis_left = self.target_landmarks['left']['PSIS']
        psis_right = self.target_landmarks['right']['PSIS']
        self.target_landmarks['sacrum']['SAC'] = [((psis_left[0] + psis_right[0]) / 2),
                                           ((psis_left[1] + psis_right[1]) / 2),
                                           ((psis_left[2] + psis_right[2]) / 2)]

    def update_source_landmarks_dict(self):
        # SSM fitted landmark coordinates
        if self.ll_model.side == 'left':
            model_list = [self.ll_model.ll_l]
        elif self.ll_model.side == 'right':
            model_list = [self.ll_model.ll_r]
        else:
            model_list = [self.ll_model.ll_l, self.ll_model.ll_r]
        for model in model_list:
            side = model.side
            for landmark_name in self.landmark_names_to_fit:
                for key in model.pelvis_model.landmark_coords['left'].keys():
                    if landmark_name in key:
                        self.source_landmarks['left'].update(
                            {landmark_name: model.pelvis_model.landmark_coords['left'][key]})
                for key in model.pelvis_model.landmark_coords['right'].keys():
                    if landmark_name in key:
                        self.source_landmarks['right'].update(
                            {landmark_name: model.pelvis_model.landmark_coords['right'][key]})
                for key in model.femur_model.landmark_coords[side].keys():
                    if landmark_name in key:
                        self.source_landmarks[side].update(
                            {landmark_name: model.femur_model.landmark_coords[side][key]})
                for key in model.tibfib_model.landmark_coords[side].keys():
                    if landmark_name in key:
                        self.source_landmarks[side].update(
                            {landmark_name: model.tibfib_model.landmark_coords[side][key]})
                if model.include_patella:
                    for key in model.patella_model.landmark_coords[side].keys():
                        if landmark_name in key:
                            self.source_landmarks[side].update(
                                {landmark_name: model.patella_model.landmark_coords[side][key]})

            psis_left = self.source_landmarks['left']['PSIS']
            psis_right = self.source_landmarks['right']['PSIS']
            self.source_landmarks['sacrum']['SAC'] = [((psis_left[0] + psis_right[0]) / 2),
                                               ((psis_left[1] + psis_right[1]) / 2),
                                               ((psis_left[2] + psis_right[2]) / 2)]

    def obtain_landmark_lists_from_dict(self):
        target_lms_list = []
        source_lms_list = []
        if self.side == 'both':
            for side in ['left', 'right']:
                for landmark_name in self.landmark_names_to_fit:
                    target_lms_list.append(self.target_landmarks[side][landmark_name])
                    source_lms_list.append(self.source_landmarks[side][landmark_name])
        else:
            for landmark_name in self.landmark_names_to_fit:
                target_lms_list.append(self.target_landmarks[self.side][landmark_name])
                source_lms_list.append(self.source_landmarks[self.side][landmark_name])
            if self.side == 'left':
                target_lms_list.append(self.target_landmarks['right']['ASIS'])
                target_lms_list.append(self.target_landmarks['right']['PSIS'])
                source_lms_list.append(self.source_landmarks['right']['ASIS'])
                source_lms_list.append(self.source_landmarks['right']['PSIS'])
            elif self.side == 'right':
                target_lms_list.append(self.target_landmarks['left']['ASIS'])
                target_lms_list.append(self.target_landmarks['left']['PSIS'])
                source_lms_list.append(self.source_landmarks['left']['ASIS'])
                source_lms_list.append(self.source_landmarks['left']['PSIS'])
        return target_lms_list, source_lms_list
