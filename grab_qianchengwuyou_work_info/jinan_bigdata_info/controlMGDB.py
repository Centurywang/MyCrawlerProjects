import pymongo

class Control_MGDB:
    def __init__(self,url):
        self.myclient = pymongo.MongoClient(url)

    def create_database(self,db_name='runood'):
        '''创建数据库'''
        mydb = self.myclient[db_name]

    def judge_database(self,db_name='runood'):
        '''判断数据库是否存在'''
        dblist = self.myclient.list_database_names()
        if db_name in dblist:
            print('数据库{}存在'.format(db_name))
        else:
            print('数据库{}不存在'.format(db_name))

    def create_sets(self,db_name,sets_name):
        '''创建集合'''
        mydb = self.myclient[db_name]
        mycol = mydb[sets_name]

    def judge_sets(self,db_name,sets_name):
        '''判断集合是否存在'''
        mydb = self.myclient[db_name]
        collist = mydb.list_collection_names()
        if sets_name in collist:
            print('集合{}存在'.format(sets_name))
        else:
            print('集合{}不存在'.format(sets_name))

    def insert_one_document(self,db_name,sets_name,data):
        '''向集合插入单个文档'''
        mydb = self.myclient[db_name]
        mycol = mydb[sets_name]
        x = mycol.insert_one(data)
        return x.inserted_id    # 返回_id字段

    def insert_documents(self,db_name,sets_name,data):
        '''向集合插入多个文档
            注：指定id插入dataList中数据为：
                { "_id": 1, "name": "RUNOOB", "cn_name": "菜鸟教程"}
        '''
        mydb = self.myclient[db_name]
        mycol = mydb[sets_name]
        x = mycol.insert_many(data)
        return x.inserted_ids

    def select_condition_data(self,db_name,sets_name,condition=None,limitNumber=None,specifiedField=None,sortOrd=None):
        '''根据指定条件查询集合中数据
            参数：
                db_name 数据库名,sets_name 集合名,condition=None 查询条件,limitNumber=None 查询数目,specifiedField 指定返回字段,sortOrd  字段和排序方式(1升序,2降序)
        '''
        mydb = self.myclient[db_name]
        mycol = mydb[sets_name]
        all_data = [x for x in mycol.find(condition, specifiedField)]
        if sortOrd is not None:
            all_data = [x for x in mycol.find(condition, specifiedField).sort(sortOrd[0], sortOrd[1])]
        if limitNumber is not None:
            all_data = [x for x in mycol.find(condition, specifiedField).limit(limitNumber)]
            if sortOrd is not None:
                all_data = [x for x in mycol.find(condition, specifiedField).sort(sortOrd[0], sortOrd[1]).limit(limitNumber)]
        return all_data

    def alter_one_document(self,db_name,sets_name,condition,newValue):
        '''修改一个文档'''
        mydb = self.myclient[db_name]
        mycol = mydb[sets_name]
        newValue = {"$set":newValue}
        mycol.update_one(condition,newValue)

    def alter_many_documents(self,db_name,sets_name,newValues,conditions):
        '''修改所有匹配到的记录'''
        mydb = self.myclient[db_name]
        mycol = mydb[sets_name]
        newValue = {"$set": newValues}
        mycol.update_many(conditions, newValue)

    def delete_one_document(self,db_name,sets_name,condition):
        '''删除一个数据'''
        mydb = self.myclient[db_name]
        mycol = mydb[sets_name]
        mycol.delete_one(condition)

    def delete_condition_documents(self,db_name,sets_name,condition):
        '''删除所有匹配数据
            condition为 {} 删除所有数据
        '''
        mydb = self.myclient[db_name]
        mycol = mydb[sets_name]
        x = mycol.delete_many(condition)
        if condition == {}:
            print('删除所有数据，共%d条'%x.deleted_count)

    def drop_sets(self,db_name,sets_name):
        '''删除一个集合'''
        mydb = self.myclient[db_name]
        mycol = mydb[sets_name]
        mycol.drop()

if __name__ == '__main__':
    db = Control_MGDB('mongodb://localhost:27017/')
    # db.insert_documents(db_name='runoob',sets_name='sites',dataList=[
    #                       { "_id": 1, "name": "RUNOOB", "cn_name": "菜鸟教程"},
    #                       { "_id": 2, "name": "Google", "address": "Google 搜索"},
    #                       { "_id": 3, "name": "Facebook", "address": "脸书"},
    #                       { "_id": 4, "name": "Taobao", "address": "淘宝"},
    #                       { "_id": 5, "name": "Zhihu", "address": "知乎"}
    #                     ])
    #print(db.select_all_data(db_name='runoob',sets_name='sites',condition={'_id':1}))
    #print(db.select_condition_data(db_name='runoob',sets_name='sites',condition={"cn_name": "菜鸟教程"},limitNumber=1,specifiedField={'_id':1}))
    #db.alter_one_document(db_name='runoob',sets_name='sites',condition={"cn_name": "菜鸟教程"},newValue={"cn_name": "菜鸟"})
    #db.alter_many_documents(db_name='runoob',sets_name='sites',conditions={ "name": { "$regex": "^F" } },newValues={'name':'脸书'})
    #print(db.select_condition_data(db_name='runoob',sets_name='sites'))
    #print(db.select_condition_data(db_name='runoob',sets_name='sites',sortOrd=('_id',-1),limitNumber=3))
    #db.drop_sets(db_name='runoob',sets_name='sites')
    #db.judge_sets(db_name='runoob',sets_name='sites')