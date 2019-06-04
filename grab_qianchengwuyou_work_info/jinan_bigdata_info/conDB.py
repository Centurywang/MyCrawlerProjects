import pymysql

class ConDB:
    def __init__(self,ip,username,password):
        # 打开数据库连接
        # 注意 此处填写自己的ip地址 用户名 密码
        self.db = pymysql.connect(ip,username, password)
        # 使用 cursor() 方法创建一个游标对象 cursor
        self.cursor = self.db.cursor()
    def execute_sql(self,sql):
        '''执行插入操作sql语句'''
        # 使用 execute() 方法执行 SQL
        try:
            # 选择数据库
            # 注意 此处填写自己的数据库名
            self.cursor.execute('use 数据库名')
            # 执行sql语句
            self.cursor.execute(sql)
            # 提交到数据库执行
            self.db.commit()
        except Exception as e:
            print(e)
            # 如果发生错误则回滚
            self.db.rollback()

    def __del__(self):
        # 关闭数据库连接
        self.db.close()