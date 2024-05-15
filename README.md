
<img src="http://www.yxgeneral.cn/prts.png" width="200" height="200" style="float:right"/>

![](https://img.shields.io/badge/Project-Visindigo-purple)
![](https://img.shields.io/badge/Python-3.8%2B-blue)
![](https://img.shields.io/badge/PySide6-6.5%2B-lightgreen)
![](https://img.shields.io/badge/PySide2-5.15%2B-lightgreen)
![](https://img.shields.io/badge/LGPL-2.1-green)

PRTS is a lightweight permission, role and token management system for website backends, application backends, etc.

PRTS uses the built-in sqlite3 module of Python to operate the database, and the SQL statements used are all standard statements. Therefore, if necessary, you can directly migrate the database operation implementation of PRTS to other databases.

# Features
- Role (User) Management
  - Basic registration, login, etc.
  - **Password supports hash encrypted storage with salt added**
  - STMP email binding
  - User nickname setting, etc.
  - Other user information that can be freely configured
- Permission Management
  - Permission system represented by strings
  - Permission group and permission inheritance
  - Permissions with expiration marks
- Token Management
  - Generate and verify tokens
  - Tokens with expiration marks
- Product activation key management
  - Generate and verify activation keys
  - Perform different operations according to the todo information carried by the key
  - Keys that can be used in batches
  - Keys with expiration marks
- Regular schedule facility
  - Can specify the schedule time in a more complex way with wildcards
  - Built-in a schedule `PRTSClearExpiredSchedule` that cleans the database every 10 minutes
  - Built-in a server guardian as an example, which sends a request to a specific URL every minute `PRTSServerGuardian`
  - **It is worth noting that the internal of the regular schedule facility uses multi-threading, so you need to pay attention to thread safety issues when using it. Please refer to the document for details.**

# Installation & Usage
Clone this repository or just download the code, then copy the `PRTS` folder to your project directory.

To use PRTS, you just need to import the `PRTS` module in your Python code:
```python
from PRTS import *

PRTS()
```
We recommend that do not use any variable to store the return value of `PRTS()`, because the `PRTS` class is a singleton class, just use `PRTS.Instance` to access the instance of `PRTS`.

For more details, please refer to the [document](doc/README.md).

# ProductKey TODO
The ProductKey management system of PRTS can be used to activate software, and in order to facilitate the activation of different products according to different keys (anyway, just execute different operations as needed), the key management system of PRTS will carry a TODO information in each key, the content of which is any string, and different operations can be performed according to the TODO information during activation.

For example, you can use `PRTS.TempStringManager.generatProductKey()` to generate a key. To call this function, you need the following parameters:
- todo: str, the TODO information carried by the key
- count: int, the number of times this key can be used
- ttl: int, the validity period of this key, in seconds

Then this function will return the string as the key.

When you need to verify the key, you can use `PRTS.TempStringManager.verifyProductKey()`, this function requires the following parameters:
- key: str, the key to be verified
- username: str, the user to be verified

This function will return a bool value, indicating whether the key is valid. If it is valid, this function will try to call the TODO parsing function, which requires you to inherit the `PRTS.ProductKeyTODOHandler` class and implement the `handle()` method in it. This method requires the following parameters:
- key: str, the key to be verified
- username: str, the user who activated this key
- todo: str, the TODO information carried by the key
- count: int, the number of times this key can be used
- ttl: int, the validity period of this key, in seconds
- spawn_time: int, the generation time of this key, in seconds

This function should return a bool value indicating whether the operation was successful.

To connect the TODOHandler to PRTS, just call `PRTS.ProductKeyManager.setTODOHandler()`.

# Functions for debugging
When you can use PySide2 or PySide6, you can use PRTS.GUI for visual operations.
> It should be noted that PRTS.GUI is only used for debugging and should not be used in production environments. At the same time, the code that imports PySide2 is commented out by default. If your Python version does not support Qt6, you should uncomment the import of PySide2 in `PRTS.GUI._QtGeneral.py`.

# Acknowledgement
This project's source code evolved from the login system source code of the [ECS](http://ecs.yxgeneral.cn) project, and some of the requirements and implementations also refer to the [C_SAT](https://c-sat.processsafetytool.com/#/login) project.
(Both of these are written by me, so I thank myself XD)


