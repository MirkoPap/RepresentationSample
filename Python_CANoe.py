# coding: utf-8
"""API for setup/usage of Canoe COM Client interface.
added function for test execution

preconditions:
1) CANoe 12 installed and available demo configuration
@ C:\Users\Public\Documents\Vector\CANoe\Sample Configurations 12.0.189\
CAN\CANSystemDemo\CANSystemDemo.cfg
2) python 3.7 or higher
"""
# --------------------------------------------------------------------------
# Standard library imports
import os
import sys
import subprocess
# import win32com.client
import time
import threading
from win32com.client import *
from win32com.client.connect import *



# Vector Canoe Class
class CANoe:
    def __init__(self):
        self.application = None
        # check if there is any instance of CANoe process
        # output = subprocess.check_output('tasklist', shell=True)
        # if CANoe process is still available, kill the process
        # if "CANoe32.exe" in str(output):
        #     os.system("taskkill /im CANoe32.exe /f 2>nul >nul")

        # re-dispatch object for CANoe Application
        self.application = win32com.client.DispatchEx("CANoe.Application")
        self.ver = self.application.Version
        print('Loaded CANoe version ',
            self.ver.major, '.',
            self.ver.minor, '.',
            self.ver.Build, '...')#, sep,''

        self.Measurement = self.application.Measurement.Running
        print(self.Measurement)


    def open_simulation(self, cfgname):
        # open CANoe simulation
        if (self.application != None):
            # check for valid file and it is *.cfg file
            if os.path.isfile(cfgname) and (os.path.splitext(cfgname)[1] == ".cfg"):
                self.application.Open(cfgname)
            else:
                raise RuntimeError("Can't find CANoe cfg file")
        else:
            raise RuntimeError("CANoe Application is missing,unable to open simulation")

    def close_simulation(self):
        # close CANoe simulation
        if (self.application != None):
            self.stop_Measurement()
            self.application.Quit()

        # make sure the CANoe is close properly, otherwise enforce taskkill
        output = subprocess.check_output('tasklist', shell=True)

        if "CANoe32.exe" in str(output):
            os.system("taskkill /im CANoe32.exe /f 2>nul >nul")

        self.application = None

    def start_Measurement(self):
        retry = 0
        retry_counter = 5
        # try to establish measurement within 20s timeout
        while not self.application.Measurement.Running and (retry < retry_counter):
            self.application.Measurement.Start()
            time.sleep(1)
            retry += 1
        if (retry == retry_counter):
            raise RuntimeWarning("CANoe start measuremet failed, Please Check Connection!")

    def stop_Measurement(self):
        if self.application.Measurement.Running:
            self.application.Measurement.Stop()
        else:
            pass

    def get_EnvVar(self, var):

        if (self.application != None):
            result = self.application.Environment.GetVariable(var)
            return result.Value
        else:
            raise RuntimeError("CANoe is not open,unable to GetVariable")

    def set_EnvVar(self, var, value):
        result = None

        if (self.application != None):
            # set the environment varible
            result = self.application.Environment.GetVariable(var)
            result.Value = value

            checker = self.get_EnvVar(var)
            # check the environment varible is set properly?
            while (checker != value):
                checker = self.get_EnvVar(var)
        else:
            raise RuntimeError("CANoe is not open,unable to SetVariable")

    def get_SigVal(self, channel_num, msg_name, sig_name, bus_type="CAN"):
        """
        @summary Get the value of a raw CAN signal on the CAN simulation bus
        @param channel_num - Integer value to indicate from which channel we will read the signal, usually start from 1,
                             Check with CANoe can channel setup.
        @param msg_name - String value that indicate the message name to which the signal belong. Check DBC setup.
        @param sig_name - String value of the signal to be read
        @param bus_type - String value of the bus type - e.g. "CAN", "LIN" and etc.
        @return The CAN signal value in floating point value.
                Even if the signal is of integer type, we will still return by
                floating point value.
        @exception None
        """
        if (self.application != None):
            result = self.application.GetBus(bus_type).GetSignal(channel_num, msg_name, sig_name)
            return result.Value
        else:
            raise RuntimeError("CANoe is not open,unable to GetVariable")

    def get_SysVar(self, ns_name, sysvar_name):

        if (self.application != None):
            systemCAN = self.application.System.Namespaces
            sys_namespace = systemCAN(ns_name)
            sys_value = sys_namespace.Variables(sysvar_name)
            return sys_value.Value
        else:
            raise RuntimeError("CANoe is not open,unable to GetVariable")

    def set_SysVar(self, ns_name, sysvar_name, var):

        if (self.application != None):
            systemCAN = self.application.System.Namespaces
            sys_namespace = systemCAN(ns_name)
            sys_value = sys_namespace.Variables(sysvar_name)
            sys_value.Value = var
            # print(sys_value)
            # result = sys_value(sys_name)
            #
            # result = var
        else:
            raise RuntimeError("CANoe is not open,unable to GetVariable")

    def get_all_SysVar(self, ns_name):

        if (self.application != None):
            sysvars=[]
            systemCAN = self.application.System.Namespaces
            sys_namespace = systemCAN(ns_name)
            sys_value = sys_namespace.Variables
            for sys in sys_value:
                sysvars.append(sys.Name)
                sysvars.append(sys.Value)
            return sysvars
        else:
            raise RuntimeError("CANoe is not open,unable to GetVariable")

    def exe_TestModule(self, envName, testModuleName):
    """ function that executes a testModule based on the given test environment
    and test module name
    IMPORTANT NOTICE: due to bug in object.Name return value with trailing 
    symbols its mandatory to use .rstrip() before usage of that value"""
            if (self.application != None):
                testEnvironments = self.application.Configuration.TestSetup.TestEnvironments
                
                for each in testEnvironments:
                    if each.Name.rstrip()== envName:
                        testEnv = each
                        break
                    else:
                        RuntimeError("CANoe is not open,unable to start Test")      
                #print ("testEVN: ",testEnvironments)
                #testEnv = testEnvironments(envName)
                #print("testEnvName:", testEnv.Name)
                
                allTestModules = testEnv.TestModules
                                
                for each in allTestModules:
                """ .rstrip() used due to trailing symbols in return str value
                of object.Name"""
                    # print(type(each.Name))
                    # print(type(testModuleName))
                    # print("1",each.Name, "1")
                    # print("1",testModuleName,"1") 
                    if each.Name.rstrip() == testModuleName:
                        print("starting the test", testModuleName)
                        each.Start()
                        break
                    else:
                        RuntimeError("strings didnt match, Test Module with name ",
                        testModuleName,"does not exist in the TestEnv")      
            else:
                raise RuntimeError("CANoe is not open,unable to start Test")
        
#On Event Thread
class Event_Job(threading.Thread):

    def __init__(self, name,var,event):#*args, **kwargs
        super(Event_Job, self).__init__()#*args, **kwargs
        self.__flag = threading.Event()     # 用于暂停线程的标识
        self.__flag.set()       # 设置为True
        self.__running = threading.Event()      # 用于停止线程的标识
        self.__running.set()      # 将running设置为True

        self.name = name
        self.var = var
        self.event = event

    def run(self):
        pythoncom.CoInitialize()
        self.app = DispatchEx('CANoe.Application')
        self.systemCAN = self.app.System.Namespaces
        self.sys_namespace = self.systemCAN(self.name)
        self.sys_value = self.sys_namespace.Variables
        self.result = self.sys_value(self.var)
        WithEvents(self.result, self.event)

        while self.__running.isSet():
            self.__flag.wait()      # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            # self.func(self.txt)
            # print time.time()
            # pythoncom.CoInitialize()
            pythoncom.PumpWaitingMessages()
            time.sleep(0.01)
            # pythoncom.CoUninitialize()

    def pause(self):
        self.__flag.clear()     # 设置为False, 让线程阻塞

    def resume(self):
        self.__flag.set()    # 设置为True, 让线程停止阻塞

    def stop(self):
        self.__flag.set()       # 将线程从暂停状态恢复, 如何已经暂停的话
        self.__running.clear()        # 设置为False
        pythoncom.CoUninitialize()

class MFL_volplus_Events(object):
    def __init__(self):
        pass

    """Handler for CANoe var events"""
    def OnChange(self,value):
        # self.Changed = True
        print("< MFL_volplus_Events var change>")
        # print(self.Name)
        print(value)

class MFL_volminus_Events(object):
    def __init__(self):
        pass

    """Handler for CANoe var events"""
    def OnChange(self,value):
        # self.Changed = True
        print("< MFL_volminus_Events var change>")
        # print(self.Name)
        print(value)


# #Regserver COM API
# os.chdir("C:\Program Files (x86)\Vector CANoe 9.0\Exec32")
# os.popen("canoe32 -regserver").readlines()
# #or
# os.chdir("C:\Program Files\Vector CANoe 10.0\Exec64")
# os.popen("canoe64 -regserver").readlines()

# app = CANoe()
# time.sleep(5111)
# app.start_Measurement()
# time.sleep(5)
# app.stop_Measurement()
# time.sleep(1111)
# varnames = app.get_all_SysVar("mfl")
#
# time.sleep(1)
# vol_plus = Event_Job("mfl","vol_plus",MFL_volplus_Events)
# vol_plus.start()
#
# vol_minus = Event_Job("mfl","vol_minus",MFL_volminus_Events)
# vol_minus.start()
#
# time.sleep(31)
# app.set_SysVar("mfl","vol_plus",1)
#
# print(app.get_SysVar("mfl","vol_plus"))
#
# vol_plus.stop()
# vol_minus.stop()

def main():
    '''
    Simple example of usage CANoe python API for automation of test execution
    '''
    canoePath = os.path.join("C:\\","Users","Public","Documents","Vector","CANoe")
    #print("canoePath =", canoePath)
    samplePathCfg = os.path.join(canoePath,"Sample Configurations 12.0.189")
    #print("sample path =", samplePathCfg)
    canSystemDemoPath = os.path.join(samplePathCfg,"CAN","CANSystemDemo")
    #print("canSystemDemoPath path =", canSystemDemoPath,)
    fullCANoeCfgPath = os.path.join(canSystemDemoPath,"CANSystemDemo.cfg")
    abs_cfg_path = os.path.abspath(fullCANoeCfgPath)
    print("abs_cfg_path path =", abs_cfg_path)
    
    print("Starting CANoe application!")
    app = CANoe()
    time.sleep(10)
    print("opening configuration!")
    app.open_simulation(abs_cfg_path)
    time.sleep(10)
    print("starting measurement!")
    app.start_Measurement()
    time.sleep(10)
    print("executing test module!")
    app.exe_TestModule("Test Environment", "Engine Tester")
if __name__ == "__main__":
    main()
