typedef i64 int

include "exception.thrift"

struct ReadMetaData {
    1:string ip; // DN服务的IP
    2:i32 port; // DN服务所在端口号
    3:int id; // 文件块的ID
    4:int offset; // 文件块起始位置相对于文件的偏移
    5:int length; // 文件块的长度
}

struct WriteMetaData {
    1:string ip; // DN服务所在Ip
    2:i32 port; // DN服务端口号
    3:int id; // 文件块ID
    4:int offset; // 开始写的位置相对于该文件块的偏移
    5:int length; // 可写的总长度
}

enum WriteMode {
    Overwrite = 1,
    Append = 2
}