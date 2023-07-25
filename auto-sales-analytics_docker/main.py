from scripts._common import save_to_excel
from scripts.abc_analysis import perform_abc
from scripts.xyz_analysis import perform_xyz


def main():
    data_path = "/app/data/sales.csv"

    # ABC analysis
    abc_result = perform_abc(data_path)
    save_to_excel(abc_result, file_name="ABC")

    # XYZ analysis
    xyz_result = perform_xyz(data_path)
    save_to_excel(xyz_result, file_name="XYZ")


if __name__ == "__main__":
    main()
