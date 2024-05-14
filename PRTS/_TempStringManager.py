from typing import *
from sqlite3 import *
from ._Utils import *
from ._Config import *
import time

class ProductKeyTODOHandler:
    def handler(this, key:str, username:str, todo:str, count:int, ttl:int, spawn_time:int)->bool:
        pass

class PRTSTempStringManager:
    """
    # verifycode
    | username | code | ttl | spawn_time |
    | -------- | ---- | --- | ---------- |
    | Text     | Text | Int | Int        |
    # token
    | username | token | ttl | spawn_time |
    | -------- | ----- | --- | ---------- |
    | Text     | Text  | Int | Int        |
    # productKey
    | key | todo | count | ttl | spawn_time |
    | --- | ---- | ----- | --- | ---------- |
    | Text| Text | Int   | Int | Int        |
    # permission_group
    | groupname | permission | ttl |
    | --------- | ---------- | --- |
    | Text      | Text       | Int |
    # permission
    | username | permission | ttl | spawn_time |
    | -------- | ---------- | --- | ---------- |
    | Text     | Text       | Int | Int        |
    """
    DataBasePath: str
    DataBase: Connection
    DBCursor: Cursor
    ProductKeyTodo: ProductKeyTODOHandler
    def __init__(this):
        this.DataBasePath = PRTSConfig.Instance["DataBase"]["FileFolder"] + "/prts_tempstring.db"
        this.DataBase = connect(this.DataBasePath, isolation_level=None, check_same_thread=False)
        this.DataBase.execute("CREATE TABLE IF NOT EXISTS verifycode \
(username TEXT, code TEXT, ttl INTEGER, spawn_time INTEGER)")
        this.DataBase.execute("CREATE TABLE IF NOT EXISTS token \
(username TEXT, token TEXT, ttl INTEGER, spawn_time INTEGER)")
        this.DataBase.execute("CREATE TABLE IF NOT EXISTS productKey \
(key TEXT, todo TEXT, count INTEGER, ttl INTEGER, spawn_time INTEGER)")
        this.DataBase.execute("CREATE TABLE IF NOT EXISTS permission_group \
(groupname TEXT, permission Text, ttl INTEGER)")
        this.DataBase.execute("CREATE TABLE IF NOT EXISTS permission \
(username TEXT, permission Text, ttl INTEGER, spawn_time INTEGER)")
        this.ProductKeyTodo = ProductKeyTODOHandler()
    
    def clearExipred(this):
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("DELETE FROM verifycode WHERE spawn_time + ttl < ?", (time.time(),))
        dbCursor.execute("DELETE FROM token WHERE spawn_time + ttl < ?", (time.time(),))
        dbCursor.execute("DELETE FROM productKey WHERE spawn_time + ttl < ?", (time.time(),))
        dbCursor.execute("DELETE FROM permission WHERE spawn_time + ttl < ?", (time.time(),))

    def getVerifyCode(this, username:str)->Tuple[StateCode, str]:
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT code, ttl, spawn_time FROM verifycode WHERE username=?", (username,))
        result = dbCursor.fetchone()
        if result != None:
            dbCursor.execute("DELETE FROM verifycode WHERE username=?", (username,))
        VCode:str = PRTSUtils.getRandomStr(PRTSConfig.Instance["AccountManager"]["VerifyCodeLength"])
        dbCursor.execute("INSERT INTO verifycode VALUES (?, ?, ?, ?)", (username, VCode, 
                PRTSConfig.Instance["AccountManager"]["VerifyCodeExpireTime"], 
                time.time())
            )
        return StateCode.Success, VCode
    
    def checkVerifyCode(this, username:str, verifyCode:str)->(StateCode):
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT code, ttl, spawn_time FROM verifycode WHERE username=?", (username,))
        result = dbCursor.fetchone()
        if result == None:
            return StateCode.VerifyCodeExpired
        if result[0] != verifyCode:
            return StateCode.VerifyCodeNotMatch
        if result[2] + result[1] < time.time():
            dbCursor.execute("DELETE FROM verifycode WHERE username=?", (username,))
            return StateCode.VerifyCodeExpired
        else:
            dbCursor.execute("DELETE FROM verifycode WHERE username=?", (username,))
            return StateCode.Success
    
    def getToken(this, username:str)->(str):
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("DELETE FROM token WHERE username=?", (username,))
        Token:str = PRTSUtils.getRandomStr(PRTSConfig.Instance["AccountManager"]["TokenLength"])
        dbCursor.execute("INSERT INTO token VALUES (?, ?, ?, ?)", (username, Token, 
                PRTSConfig.Instance["AccountManager"]["TokenExpireTime"],
                time.time())
            )
        return Token
    
    def checkToken(this, username:str, token:str)->Tuple[StateCode, str]:
        """
        # checkToken
        This function is designed for refreshing the token when the token is not expired.
        If the token is expired, the function will return `StateCode.TokenExpired`.
        If you want to refresh the spawn_time of the token instead of generating a new token, 
        please use `tokenAuth`.
        """
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT token, ttl, spawn_time FROM token WHERE username=?", (username,))
        result = dbCursor.fetchone()
        if result == None:
            return StateCode.TokenExpired, ""

        if result[2] + result[1] < time.time():
            return StateCode.TokenExpired, ""
        else:
            # remove the old token
            if result[0] != token:
                return StateCode.TokenExpired, ""
            dbCursor.execute("DELETE FROM token WHERE username=?", (username,))
        Token:str = PRTSUtils.getRandomStr(PRTSConfig.Instance["AccountManager"]["TokenLength"])
        dbCursor.execute("INSERT INTO token VALUES (?, ?, ?, ?)", (username, Token, 
                PRTSConfig.Instance["AccountManager"]["TokenExpireTime"],
                time.time())
            )
        return StateCode.Success, Token
    
    def tokenAuth(this, username:str, token:str)->(StateCode):
        """
        # tokenAuth
        This function is designed for refreshing the spawn_time of the token.
        If the token is expired, the function will return `StateCode.TokenExpired`.
        If you want to generate a new token instead of refreshing the spawn_time of the token,
        please use `checkToken`.
        """
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT token, ttl, spawn_time FROM token WHERE username=?", (username,))
        result = dbCursor.fetchone()
        if result == None:
            return StateCode.TokenExpired
        if result[0] != token:
            return StateCode.TokenExpired
        if result[2] + result[1] < time.time():
            return StateCode.TokenExpired
        else:
            dbCursor.execute("UPDATE token SET spawn_time=? WHERE username=?", (time.time(), username))
            return StateCode.Success
        
    
    def generateProductKey(this, todo:str, count:int, ttl:int)->str:
        dbCursor = this.DataBase.cursor()
        len = PRTSConfig.Instance["ProductKey"]["Length"]
        part = PRTSConfig.Instance["ProductKey"]["Part"]
        ProductKey:str = PRTSUtils.getRandomStr(len*part)
        # every 5 char insert a "-"
        ProductKey = "-".join([ProductKey[i:i+len] for i in range(0, len(ProductKey), len)])
        dbCursor.execute("INSERT INTO productKey VALUES (?, ?, ?, ?, ?)", (ProductKey, todo, count, ttl, time.time()))
        return ProductKey
    
    def checkProductKey(this, key:str, username:str)->StateCode:
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT todo, count, ttl, spawn_time FROM productKey WHERE key=?", (key,))
        result = dbCursor.fetchone()
        if result == None:
            return StateCode.UnknownError
        if result[1] <= 0:
            dbCursor.execute("DELETE FROM productKey WHERE key=?", (key,))
            return StateCode.UnknownError
        if result[3] + result[2] < time.time():
            dbCursor.execute("DELETE FROM productKey WHERE key=?", (key,))
            return StateCode.UnknownError
        if this.ProductKeyTodo.handler(key, username, result[0], result[1], result[2], result[3]):
            dbCursor.execute("UPDATE productKey SET count=count-1 WHERE key=?", (key,))
            return StateCode.Success
        return StateCode.UnknownError

    
    def addPermissionForGroup(this, groupname:str, permission:str, ttl:int)->StateCode:
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT ttl \
FROM permission_group WHERE groupname=? AND permission=?", (groupname, permission))
        result = dbCursor.fetchone()
        if result != None:
            dbCursor.execute("DELETE FROM permission_group WHERE groupname=? AND permission=?", (groupname, permission))
        dbCursor.execute("INSERT INTO permission_group VALUES (?, ?, ?)", (groupname, permission, ttl))
        return StateCode.Success
    
    def removePermissionForGroup(this, groupname:str, permission:str)->StateCode:
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("DELETE FROM permission_group WHERE groupname=? AND permission=?", (groupname, permission))
        return StateCode.Success
    
    def checkPermissionForGroup(this, groupname:str, permission:str, spawn_time:int)->StateCode:
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT ttl \
FROM permission_group WHERE groupname=? AND permission=?", (groupname, permission))
        result = dbCursor.fetchone()
        if result == None:
            # 获取此权限组中的所有以"group."开头的权限为组名，以递归的方式检查权限
            dbCursor.execute("SELECT permission, ttl FROM permission_group \
WHERE groupname=? AND permission LIKE 'group.%'", (groupname,))
            result = dbCursor.fetchall()
            for i in result:
                if this.checkPermissionForGroup(i[0][6:], permission, spawn_time) == StateCode.Success:
                    return StateCode.Success
            return StateCode.PermissionDenied
        if result[0] + spawn_time < time.time():
            dbCursor.execute("DELETE FROM permission_group WHERE groupname=? AND permission=?", (groupname, permission))
            return StateCode.PermissionDenied
        return StateCode.Success
        
    def checkPermission(this, username:str, permission:str)->StateCode:
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT ttl, spawn_time \
FROM permission WHERE username=? AND permission=?", (username, permission))
        result = dbCursor.fetchone()
        if result == None:
            dbCursor.execute("SELECT permission, ttl, spawn_time FROM permission \
WHERE username=? AND permission LIKE 'group.%'", (username,))
            result = dbCursor.fetchall()
            for i in result:
                if this.checkPermissionForGroup(i[0][6:], permission, i[2]) == StateCode.Success:
                    return StateCode.Success
            return StateCode.PermissionDenied
        if result[1] + result[0] < time.time():
            dbCursor.execute("DELETE FROM permission WHERE username=? AND permission=?", (username, permission))
            return StateCode.PermissionDenied
        return StateCode.Success
    
    def addPermission(this, username:str, permission:str, ttl:int)->StateCode:
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT ttl, spawn_time \
FROM permission WHERE username=? AND permission=?", (username, permission))
        result = dbCursor.fetchone()
        if result != None:
            dbCursor.execute("DELETE FROM permission WHERE username=? AND permission=?", (username, permission))
        dbCursor.execute("INSERT INTO permission VALUES (?, ?, ?, ?)", (username, permission, ttl, time.time()))
        return StateCode.Success
    
    def removePermission(this, username:str, permission:str)->StateCode:
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("DELETE FROM permission WHERE username=? AND permission=?", (username, permission))
        return StateCode.Success
    
    
    def addPermissionGroup(this, username:str, groupname:str)->StateCode:
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT ttl, spawn_time \
FROM permission WHERE username=? AND permission=?", (username, "group."+groupname))
        result = dbCursor.fetchone()
        if result != None:
            dbCursor.execute("DELETE FROM permission WHERE username=? AND permission=?", (username, "group."+groupname))
        dbCursor.execute("INSERT INTO permission VALUES (?, ?, ?, ?)", (username, "group."+groupname, 0, time.time()))
        return StateCode.Success
    
