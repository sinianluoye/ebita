exception EfsException {
    1: required i32 code;
    2: required string message;
}

struct ReadMetaData {
    1:string ip; // DN服务的IP
    2:i32 port; // DN服务所在端口号
    3:i64 id; // 文件块的ID
    4:i64 offset; // 文件块起始位置相对于文件的偏移
    5:i64 length; // 文件块的长度
}

struct WriteMetaData {
    1:string ip; // DN服务所在Ip
    2:i32 port; // DN服务端口号
    3:i64 id; // 文件块ID
    4:i64 offset; // 开始写的位置相对于该文件块的偏移
    5:i64 length; // 可写的总长度
}

enum WriteMode {
    Overwrite = 1,
    Append = 2
}

service NameNode {
    list<ReadMetaData> get_read_meta(1:string path, 2:i64 offset, 3:i64 length),
    list<WriteMetaData> get_write_meta(1:string path, 2:WriteMode mode),
    bool confirm_write(1:i64 id, 2:WriteMode mode, 3:i64 length)
}

service DataNode {
    /**
     * block_id: 要读取的数据块id
     * offset: 要开始读取的位置(相对与该文件块)
     * length: 要读取的数据长度
     * return: 读取到的数据
     */
    binary read(1:i64 block_id, 2:i64 offset, 3:i64 length) throws (1: EfsException e),
    bool write(1:i64 block_id, 2:i64 offset, 3:i64 length, 4:binary data) throws(1: EfsException e)

}