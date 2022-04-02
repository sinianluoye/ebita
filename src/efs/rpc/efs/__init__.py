import os
import sys

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../..")
sys.path.append(BASE_DIR)

import efs.rpc.efs.DataNodeService
import efs.rpc.efs.NameNodeService

