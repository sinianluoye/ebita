
import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

import copy
import json

from efs.namenode.editlog import EditLog
from utils.algorithms import binary_search


class MetaData:
    
    SUCCESS_MESSAGE = "success"
    
    def __init__(self, edit_log:EditLog) -> None:
        self.data = {}
        self.edit_log = edit_log
    
    def __convert_path_type(self, path):
        if isinstance(path, list) or isinstance(path, tuple):
            return path
        elif isinstance(path, str):
            return path.split("/")
        else:
            raise f"unsupport access path by type {type(path)}"
    
    def __access_path(self, path):
        path = self.__convert_path_type(path)
        
        cur = self.data
        for i in range(len(path)):
            k = path[i]
            if k.startswith("/"):
                raise f"unsupport access props in path"
            if k in cur:
                cur = cur[k]
            else:
                return False, f"path {'/'.join(path[:i+1])} doesn't exists"
        return True, cur
    
    def __fix_prop_name(self, prop):
        if prop.startswith("/"):
            return prop
        else:
            return "/"+prop
    
    def get(self, path, recursive=False):
        """get all props of path

        Args:
            path (str or list): wanted path
            recursive (bool, optional): if true will return all subnodes props else just return current node. Defaults to False.
        Return:
            a tuple (True, dict) or (False, str), 
            if success, will return True and the copy of expected meta data,
            else will return False and the error message
        """
        status, cur = self.__access_path(path)
        if not status:
            return False, cur
        if recursive:
            return True, copy.deepcopy(cur)
        else:
            ret = {}
            for k in cur:
                if k.startswith("/"):
                    ret[k] = copy.deepcopy(cur[k])
            return True, ret
    
    def get_blocks(self, path, offset, length):
        status, cur = self.__access_path(path)
        if not status:
            return status, cur
        blocks = cur["/blocks"]
        l = binary_search(blocks, {"offset": offset}, lambda a,b: -1 if a["offset"] < b["offset"] else (1 if a["offset"] > b["offset"] else 0))
        r = binary_search(blocks, {"offset": offset+ length}, lambda a,b: -1 if a["offset"] < b["offset"] else (1 if a["offset"] > b["offset"] else 0))
        return blocks[l:r]
        
    def __set(self, path, prop, idxs, val):
        """_summary_

        Args:
            path (_type_): path want to set
            prop (_type_): prop name want to set
            idxs (_type_): index in props, if prop is a value type, set it to None
            val (_type_): the value want to be set

        Returns:
            _type_: (True, "success") or (False, error_message)
        """
        self.__create_path(path)
        status, cur = self.__access_path(path)
        if not status:
            return False, cur
        
        prop = self.__fix_prop_name(prop)
        if idxs is None:
            cur[prop] = val
            return True, MetaData.SUCCESS_MESSAGE
        if prop not in cur:
            return False, "can not set new props with idxs"
        else:
            cur = cur[prop]
            for i, idx in enumerate(idxs):
                if i == len(idx)-1:
                    if isinstance(cur, list) and idx == len(cur):
                        cur.append(val)
                    else:
                        cur[idx] = val
                    return True, MetaData.SUCCESS_MESSAGE
                else:
                    if (isinstance(cur, list) or isinstance(cur, tuple)) and idx >= len(cur):
                        return False, f"out of length when access idx: {idxs[:i+1]}"
                    elif idx not in cur:
                        return False, f"idx {idx[:i+1]} doesn't exists"
                    cur = cur[idx]
    
    def __create_path(self, path):
        path = self.__convert_path_type(path)
        cur = self.data
        for k in path:
            if k not in cur:
                cur[k] = {}
            cur = cur[k]
    
    def set(self, path, prop, idxs, val, log=True):
        """_summary_

        Args:
            path (_type_): path want to set
            prop (_type_): prop name want to set
            idxs (_type_): index in props, if prop is a value type, set it to None
            val (_type_): the value want to be set

        Returns:
            _type_: (True, "success") or (False, error_message)
        """
        ret, msg = self.__set(path, prop, idxs, val)
        if log and ret:
            self.edit_log.set(path, prop, idxs, val)
        return ret, msg
    
    def __delete(self, path, prop, idxs):
        path = self.__convert_path_type(path)
        if prop is None:
            if idxs is not None:
                return False, f"idxs must be None when prop is None"
            else:
                to_del = path[-1]
                path = path[:-1]
                status, cur = self.__access_path(path)
                if not status:
                    return False, cur
                if to_del in cur:
                    cur.pop(to_del)
                    return True, MetaData.SUCCESS_MESSAGE
                else:
                    return False, f"path {'/'.join(path)+'/'+to_del} doesn't exist"
        else:
            status, cur = self.__access_path(path)
            if not status:
                return False, cur
            prop = self.__fix_prop_name(prop)
            if prop not in cur:
                return False, f"prop {prop} doesn't exist in path {path}"
            if idxs is None:
                cur.pop(prop)
                return True, MetaData.SUCCESS_MESSAGE
            else:
                cur = cur[prop]
                for i, idx in enumerate(idxs):
                    if i == len(idx)-1:
                        cur.pop(idx)
                        return True, MetaData.SUCCESS_MESSAGE
                    else:
                        if (isinstance(cur, list) or isinstance(cur, tuple)) and idx >= len(cur):
                            return False, f"out of length when access idx: {idxs[:i+1]}"
                        elif idx not in cur:
                            return False, f"idx {idx[:i+1]} doesn't exists"
                        cur = cur[idx]

    def delete(self, path, prop, idxs, log=True):
        status, msg = self.__delete(path, prop, idxs)
        if log and status:
            self.edit_log.delete(path, prop, idxs)
        return status, msg    
    
    def dump(self, fp)->str:
        return json.dump(self.data, fp)
    
    def load(self, fp)->None:
        self.data = json.load(fp)