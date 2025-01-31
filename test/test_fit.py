
import os
import pandas as pd

from articulated_ssm_both_sides.MainASM import run_asm


def test(file_name):
    test_directory = os.path.dirname(__file__)
    data_directory = os.path.join(test_directory, "data")
    marker_data_path = os.path.join(data_directory, file_name)
    marker_data = pd.read_pickle(marker_data_path)
    run_asm(marker_data)


if __name__ == "__main__":
    test("marker_data_1.pkl")
    test("marker_data_2.pkl")
