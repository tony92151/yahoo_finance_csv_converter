import argparse
import logging

import pandas as pd

from source_convertor import convertor_mapping
from source_convertor.base_convertor import BaseSourceConvertor

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--convertor-type", type=str, choices=convertor_mapping.keys(), required=True
    )
    parser.add_argument("--output", type=str, required=True)
    args_, _ = parser.parse_known_args()

    output_path = args_.output

    # get loader class
    convertor_class = convertor_mapping[args_.convertor_type]
    logging.info(f"Using convertor: {convertor_class.loader_name}")

    convertor_class.add_argument(parser)
    args = parser.parse_args()

    # remove source_type and output from args
    args_dict = vars(args)
    args_dict.pop("convertor_type", None)
    args_dict.pop("output", None)

    # init convertor
    convertor: BaseSourceConvertor = convertor_class(**args_dict)

    df: pd.DataFrame = convertor.convert()

    logging.info(f"Saving to {output_path}")
    df.to_csv(output_path, index=False)
