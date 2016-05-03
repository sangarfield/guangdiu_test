import pymongo
import log
def get_collection(db_name, col_name, host = 'localhost', port = 27017, add_index = None,):
    client = pymongo.MongoClient(host, port)
    db = client[db_name]
    col = db[col_name]
    log.log_prn('db', 'Open Collection : %s' % col_name, 'NORMAL')
    #添加新索引
    if add_index != None:
        if isinstance(add_index, str):
            ret = col.create_index([(add_index, pymongo.ASCENDING)], unique = True)
            log.log_prn('db', 'Collection %s Create_Index %s' % (col_name, add_index), 'NORMAL')
        else:
            log.log_prn('db', 'add_index type not str ( %s )' % type(add_index), 'ERROR')
            return None
    return col

def insert_one_doc(col, one_data):
    ret = col.insert_one(one_data) #返回InsertOneResult(inserted_id, acknowledged)实例
    if ret != None:
        log.log_prn('db', 'insert_one_doc, inserted_id : %s' % ret.inserted_id, 'NORMAL')
        return ret
    else:
        log.log_prn('db', 'insert_one_doc failed', 'WARN')
        return None

#只适用于查找item
def find_one_doc(col, id):
    return col.find({'id':id}).count()

