from ._Schedule import *
from ._TempStringManager import *
from requests import *
from colorama import *
class test_schedu(PRTSSchedule):
    def __init__(this):
        super().__init__()
        this.setTime("18:3?")
        this.setDay("14")
        this.setMonth("01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12")
        """
        Which means this schedu will be executed every minute between 18:30 - 18:39 on the 14th of every month.        
        """

    def todo(this):
        print("Hello, World!")
        print("Now:", time.strftime("%m-%d %H:%M %A", time.localtime()))

class PRTSClearExpiredSchedule(PRTSSchedule):
    def __init__(this):
        super().__init__()
        this.setTime("??:00")
        this.setDay("??")
        this.setMonth("??")
        """
        Which means this schedu will be executed every hour on every day.
        """
    def todo(this):
        PRTSTempStringManager.Instance.clearExipred()

class PRTSServerGuardian(PRTSSchedule):
    def __init__(this):
        super().__init__()
        this.setTime("??:??")
        this.setDay("??")
        this.setMonth("??")
        """
        Which means this schedu will be executed every minutes on every day.
        """
    def todo(this):
        # try to get any response from the server.
        # We use the following hypothetical URLs as examples 
        # arknights.cv/project/Preservator
        # arknights.cv/project/Caerula_Arbor
        # arknights.cv/project/Celestial_Fulcrum
        print(Back.WHITE + Fore.BLACK + "   INSTANCE    MODE     CHANNEL  INFO                            STATUS            " + Style.RESET_ALL)
        urls = ["Preservator", "Caerula_Arbor", "Celestial_Fulcrum"]
        for i in range(len(urls)):
            try:
                response = get("arknights.cv/project/" + urls[i])
                output = str(i)+") Project  #   1       [  ] E"+str(i)+"  "+":\""+"{0:<25}".format(urls[i]+"\"")+"\t OK\t■"
                for i in output:
                    print(i, end="")
                    time.sleep(random.randint(0, 1) / 20)
                print("")
            except Exception as e:
                output = str(i)+") Project  #   1       [  ] E"+str(i)+"  "+":\""+"{0:<25}".format(urls[i]+"\"")+"\t NO SIGNAL\t■"
                for i in output:
                    print(i, end="")
                    time.sleep(random.randint(0, 1) / 20)
                print("")
            time.sleep(random.randint(3, 4))