
class FileDoesNotExist(Exception):
    """ Raised when the input file does not exist"""
    def __init__(self, file_path):
        self.message = "Input file '%s' does not exist!"% file_path
        super().__init__(self.message)
