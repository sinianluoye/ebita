NAMENODE_PORT = 7468
DATANODE_PORT = 7469
OPENIP = "0.0.0.0"
NAMENODE_THREADS = 5
import os
EDITLOG_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../logs"))
BLOCK_SIZE = 16*1024*1024