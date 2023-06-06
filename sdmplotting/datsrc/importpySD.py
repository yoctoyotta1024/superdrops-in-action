# file: importpySD.py import pySD given path is Import pySD() called

import sys

class ImportpySD:

  def __init__(self):
    # self.path2CLEO = "/Users/yoctoyotta1024/Documents/b1_springsummer2023/CLEO/"
    self.path2CLEO = "/home/m/m300950/CLEO/"
    
    sys.path.append(self.path2CLEO)
    