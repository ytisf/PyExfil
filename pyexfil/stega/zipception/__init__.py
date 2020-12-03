import os
import sys
import random

from progressbar import *
from zipfile import ZipFile

from pyexfil.includes.encryption_wrappers import PYEXFIL_DEFAULT_PASSWORD


NUMBER_OF_ITERATIONS = random.randint(1345, 6548)


def _get_files_from_dir(dir_page):
    file_paths = []
    for root, directories, files in os.walk(dir_page):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
    return file_paths


def _decompress(zip_h):
    zip_h.extractall()
    return


class Broker:
    def __init__(self, file_path, key=PYEXFIL_DEFAULT_PASSWORD):
        self.file_path = file_path
        self.key = key
        self.current_iteration = 0
        self.current_file = None
        self.end = False

    def Run(self):

        self.current_file = self.file_path

        while self.end is False:
            zipfile = ZipFile(self.current_file, "r")
            if self.key is not None:
                zipfile.setpassword(self.key)
            _decompress(zipfile)
            self.current_file = zipfile.filelist[0].filename
            self.current_iteration += 1

            if self.current_file != "True.zip" and self.current_file != "False.zip":
                self.end = True
                sys.stdout.write(
                    "Finished with %s iterations.\n" % self.current_iteration
                )


class Sender:
    def __init__(
        self, folder_path, key=PYEXFIL_DEFAULT_PASSWORD, iterations=NUMBER_OF_ITERATIONS
    ):
        self.all_files = _get_files_from_dir(folder_path)
        self.key = key
        self.iterations = iterations

    def Run(self):
        sys.stdout.write("Starting with %s iterations.\n" % self.iterations)
        widgets = [
            "Compressing: ",
            Percentage(),
            " ",
            Bar(marker="#", left="[", right="]"),
            " ",
            ETA(),
            " ",
            FileTransferSpeed(),
        ]
        pbar = ProgressBar(widgets=widgets, maxval=self.iterations)
        pbar.start()

        for i in range(1, self.iterations):
            even = i % 2 == 0
            pbar.update(i)

            with ZipFile("%s.zip" % even, "w") as zip:
                if self.key is not None:
                    zip.setpassword(bytes(self.key))

                for file in self.all_files:
                    zip.write(file)

                self.all_files = ["%s.zip" % (even)]
                try:
                    os.remove("%s.zip" % str(not even))
                except:
                    pass

        pbar.finish()
        sys.stdout.write("Completed with %s iterations.\n" % self.iterations)
