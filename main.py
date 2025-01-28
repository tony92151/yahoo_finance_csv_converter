import argparse

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
    parser.add_argument("--source-type", type=str, required=True)
    parser.add_argument("--input-csv", type=str, required=True)
    parser.add_argument("--output-csv", type=str, required=True)
    args = parser.parse_args()
