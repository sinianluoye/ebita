import json
from threading import Thread, Lock
import os


class EditLog:
    
    OP_SET = "SET"
    OP_DELETE = "DELETE"
    META_FILE_SUFFIX = ".meta"
    EDIT_LOG_FILE_SUFFIX = ".editlog"
    
    def __init__(self, base_dir) -> None:
        self.base_dir = base_dir
        self.fp = None
        self.id = 0
        self.write_lock = Lock()

    def __find_file(self):
        meta_file_id = -1
        file_list = list(os.listdir(self.base_dir))
        for filename in file_list:
            if filename.endswith(EditLog.META_FILE_SUFFIX):
                try:
                    cur_id = int(filename[:-len(EditLog.META_FILE_SUFFIX)])
                    meta_file_id = max(meta_file_id, cur_id)
                except:
                    pass
        if meta_file_id == -1:
            return None, None
        edit_log_file = f"{meta_file_id}{EditLog.EDIT_LOG_FILE_SUFFIX}"
        meta_file = f"{meta_file_id}{EditLog.META_FILE_SUFFIX}"
        if edit_log_file in file_list:
            return meta_file, edit_log_file
        else:
            return meta_file, None
    
    def __first_init(self):
        self.id = 0
        self.__reset_fp()
    
    def __reset_fp(self):
        if self.fp is not None:
            self.fp.close()
            
        edit_log_file = f"{self.id}{EditLog.EDIT_LOG_FILE_SUFFIX}"
        self.fp = open(edit_log_file, "a")
        
    
    def load(self, metadata):
        self.write_lock.acquire()
        meta_file, edit_log_file = self.__find_file()
        if not meta_file:
            metadata.data = {}
            self.__first_init()
            self.write_lock.release()
            return
        
        with open(meta_file) as fp:
            metadata.load(fp)
        
        if edit_log_file:
            with open(edit_log_file) as fp:
                for line in fp.readlines():
                    cur = json.loads(line)
                    if cur[0] == EditLog.OP_SET:
                        metadata.set(cur[1], cur[2], cur[3], cur[4], False)
                    elif cur[0] == EditLog.OP_DELETE:
                        metadata.delete(cur[1], cur[2], cur[3], False)
                        
        self.id = int(meta_file[:-len(EditLog.META_FILE_SUFFIX)])
        self.__reset_fp()
        self.write_lock.release()
        return
    
    def dump(self, metadata):
        meta_file = f"{self.id}{EditLog.META_FILE_SUFFIX}"
        self.write_lock.acquire()
        with open(meta_file, "w") as fp:
            metadata.dump(fp)
        self.id += 1
        self.__reset_fp()
        self.write_lock.release()
        
    
    def append(self, op, path, prop, idxs, val):
        if isinstance(path, str):
            path = path.split("/")
        if not prop.startswith("/"):
            prop = "/" + prop
        path.append(prop)
        if op ==  EditLog.OP_SET:
            
            to_write = json.dumps([op, path, prop, idxs, val])
        else:
            to_write = json.dumps([op, path, prop, idxs])
        self.write(to_write)

    def write(self, s):
        self.write_lock.acquire()
        self.fp.write(s)
        self.fp.write('\n')
        self.fp.flush()
        self.write_lock.release()
        
    def set(self, path, prop, idxs, val):
        self.append(EditLog.OP_SET, path, prop, idxs, val)
    
    def delete(self, path, prop, idxs):
        self.append(EditLog.OP_DELETE, path, prop, idxs, None)