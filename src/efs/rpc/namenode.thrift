include "typedef.thrift"

service NameNode {
    list<ReadMetaData> get_read_meta(1:string path, 2:int offset, 3:length),
    list<WriteMetaData> get_write_meta(1:string path, 2:WriteMode mode),
    bool confirm_write(1:int id, 2:WriteMode mode, 3:int length)

}