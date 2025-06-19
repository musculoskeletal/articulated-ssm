import os
import pandas as pd
import numpy as np

from articulated_ssm_both_sides.MainASM import run_asm


def test(file_name, demo_factors):
    test_directory = os.path.dirname(__file__)
    data_directory = os.path.join(test_directory, "data")
    marker_data_path = os.path.join(data_directory, file_name)
    # marker_data = pd.read_pickle(marker_data_path)
    marker_data = {}
    with open(marker_data_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 4:
                label = parts[0]
                coords = list(map(float, parts[1:]))
                marker_data[label] = coords

    case_name = os.path.splitext(file_name)[0]
    output_directory = os.path.join(test_directory, "_output", case_name)

    run_asm(marker_data, output_directory, demo_factors)


if __name__ == "__main__":
    # test("RCH01.pkl")
    # test("RCH05.pkl")
    # test("S1.pkl")
    # test("S2.pkl")
    test("06_1064.txt", np.array([11, 145, 41, 2, 179.5, 77.4, 71.2, 60.6, 71.5, 58.5]))

'''
Demo factors as array (could be changed to dict):
0: Age, 
1: Height, 
2: Mass, 
3: Sex (1=F, 2=M), 
4: ASIS_width, 
5: PSIS_width, 
6: epicon_width_left, 
7: malleolar_width_left, 
8: epicon_width_right, 
9: malleolar_width_right

Left model uses: Age, Height, Sex, ASIS_width, PSIS_width, left_epicon_width, left_malleolar_width
Right model uses: Age, Height, Sex, ASIS_width, PSIS_width, right_epicon_width
'''
