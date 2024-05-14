from enum import *
import random
import os
class StateCode(Enum):
    UnknownError = 0
    Success = 1
    PermissionDenied = 2
    UsernameAlreadyExists = 100
    EmailAlreadyExists = 101
    VerifyCodeNotMatch = 102
    VerifyCodeNotExpired = 103
    UsernameOrPasswordNotMatch = 104
    UnknwonUsername = 105
    UsernameInvalid = 200
    PasswordInvalid = 201
    EmailInvalid = 202
    VerifyCodeInvalid = 203
    VerifyCodeExpired = 204
    TokenInvalid = 205
    TokenExpired = 206
    ProductKeyInvalid = 207
    ProductKeyExpired = 208
    
class PRTSUtils:
    @staticmethod
    def generateRandomChar()->str:
        rNum = chr(random.randint(48, 57))
        rChar = chr(random.randint(65, 90))
        if rChar=="I":rChar="V"
        if rChar=="O":rChar="M"
        if rChar=="D":rChar="A"
        if rChar=="L":rChar="B"
        if random.randint(0,1):
            return rNum
        else:
            return rChar
    
    @staticmethod
    def getRandomStr(length:int)->str:
        result = ""
        for i in range(length):
            result += PRTSUtils.generateRandomChar()
        return result
    
    @staticmethod
    def getSizeOfFolder(folder:str)->int:
        total_size = 0
        for path, dirs, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(path, file)
                total_size += os.path.getsize(file_path)
        return total_size