import pandas as pd
from os.path import basename


def read_raw(file_paths):
    header = ["trialNr", "time", "frameAngle", "rodAngle", "current", "response"]
    data_list = []
    for file in file_paths:
        f_name = basename(file)
        name_parts = f_name.split("_")
        subject_id = name_parts[0]
        condition = name_parts[2]
        d = pd.read_csv(file, sep=", ", header=None,
                        names=header, engine="python")
        d["subject"] = subject_id
        d["condition"] = condition
        data_list.append(d)
    df = pd.concat(data_list)
    return df
