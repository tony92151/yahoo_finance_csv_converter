import argparse

from source_loader import loader_mapping

accept_source_type = ["schwab", "firstrade"]


def main(source_type: str, input_csv: str, output_csv: str):
    if source_type not in accept_source_type:
        raise ValueError(
            f"Source type {source_type} is not support. Current support {accept_source_type}"
        )

    # TODO:
    # load source loader accourding source_type
    # init source loader and convert
    # verifide the output format
    # save output to csv file


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-type", type=str, choices=loader_mapping.keys(), required=True
    )
    parser.add_argument("--history-data", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    args_, _ = parser.parse_known_args()

    # get loader class
    loader_class = loader_mapping[args_.source_type]
    loader_class.add_argument(parser)
    args = parser.parse_args()

    # remove source_type from args
    args_dict = vars(args)
    args_dict.pop("source_type", None)

    # init loader
    loader = loader_class(**args_dict)
