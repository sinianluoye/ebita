
include "typedeft.thrift"

service DataNode {
    /**
     * block_id: 要读取的数据块id
     * offset: 要开始读取的位置(相对与该文件块)
     * length: 要读取的数据长度
     * return: 读取到的数据
     */
    binary read(1:int block_id, 2:int offset, 3:int length) throws (1: EfsException e),
    bool write(`:int block_id, 2:int offset, 3:int length, 4:binary data) throws(1: EfsException e)

}