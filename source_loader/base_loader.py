class BaseSourceLoader:
    loader_name = "base_loader"

    def __init__(self, input_csv_path: str):
        # TODO:
        # check if file exist
        # load the file
        pass

    def convert(self):
        raise NotImplementedError()
