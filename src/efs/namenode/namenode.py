from threading import Thread
import threading
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
import sys
import os
from efs.namenode.editlog import EditLog

from efs.namenode.metadata import MetaData

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from config import OPENIP, NAMENODE_PORT, DATANODE_PORT,NAMENODE_THREADS, EDITLOG_DIR
import efs.rpc.efs as rpc
from efs.rpc.efs.ttypes import *

class NameNode(threading.Thread):
    
    def __init__(self, host=OPENIP, port=NAMENODE_PORT, threads=NAMENODE_THREADS, editlog_dir=EDITLOG_DIR) -> None:
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.threads = threads
        self.edit_log = EditLog(editlog_dir)
        self.meta = MetaData(self.edit_log)
        
        
    def get_read_meta(self,path, offset, length):
        blocks = self.meta.get_blocks(path, offset, length)
        return [ReadMetaData(**block) for block in blocks]
    
    def get_write_meta(self, path, mode):
        print("process get_write_meta!")
        return []
    
    def confirm_write(self, id, mode, length):
        print("process confirm_write!")
        return True
    
    def run(self):
        processor = rpc.NameNodeService.Processor(self)

        # 监听端口
        transport = TSocket.TServerSocket(host=self.host, port=self.port)

        # 选择传输层
        tfactory = TTransport.TBufferedTransportFactory()

        # 选择传输协议
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()

        # 创建服务端
        server = TServer.TThreadPoolServer(processor, transport, tfactory, pfactory)

        # 设置连接线程池数量
        server.setNumThreads(self.threads)
        print("启动NameNode")
        # 启动服务
        server.serve()
        print("退出NameNode")

    
if __name__ == "__main__":
    
    server = NameNode()
    server.start()
    
    transport = TSocket.TSocket('127.0.0.1', NAMENODE_PORT)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = rpc.NameNodeService.Client(protocol)

    # 连接服务端
    transport.open()

    recv = client.confirm_write(1,1,1)
    print(recv)

    recv = client.get_read_meta("123", 1, 2)
    print(recv)

    recv = client.get_write_meta("123", 1)
    print(recv)

    # 断连服务端
    transport.close()

