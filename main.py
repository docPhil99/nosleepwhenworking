import configparser
import sys
from pathlib import Path
import psutil
import dbus

EVENTS = {"LOGOUT": 1, "USERSWITCH": 2, "SUSPEND": 4, "IDLE": 8}

class InhitorManager:
    def __init__(self):
        bus = dbus.SessionBus()
        self.manager = dbus.Interface( bus.get_object('org.gnome.SessionManager', '/org/gnome/SessionManager'),
                                 dbus_interface='org.gnome.SessionManager')

        self.inhibit_dict={}
        #self.proc_name_list = []

    def inhibit(self,process_name,type):
        self.inhibit_dict[process_name]=SingleInhibit(process_name,type,self.manager)

    def remove(self, process_name):
        del self.inhibit_dict[process_name]

class SingleInhibit:
    def __init__(self, process_name ,type ,manager):
        self.manager = manager
        print(f'Inhibiting {process_name}')
        self._inhibit_cookie = manager.Inhibit(dbus.String(process_name), dbus.UInt32(0), dbus.String("inhibiting"), dbus.UInt32(type))

    def __del__(self):
        print('called del')
        try:
            self.manager.Uninhibit(self._inhibit_cookie)
        except Exception as a :
            print(a)



def make_default_ini(path = None):
    config = configparser.ConfigParser()
    config['DEFAULT'] = {}
    config['USERSWITCH'] = {}
    config['LOGOUT'] = {}
    config['SUSPEND'] = {'Item' : "pycharm\nDaVinciPanelDaemon\nchump"}
    config['IDLE'] = {}

    if not path:
        path = Path.home()/Path(".config")/Path("inhibitor.ini")
    try:
        with open(path, 'w') as configfile:
            config.write(configfile)
    except IOError as e:
        print(f'Failed to write to {path}')
        print(e)
        sys.exit(-1)

def read_ini(path=None):
    config = configparser.ConfigParser()
    if not path:
        path = Path.home() / Path(".config") / Path("inhibitor.ini")
    try:
        #with open(path, 'r') as configfile:
        config.read(path)
    except IOError as e:
        print(f'Failed to read {path}')
        print(e)
        sys.exit(-1)


    for sec in config.sections():
        print(sec)
        for k,v in config[sec].items():
            if k == 'item':
                subval = v.split()
                print(f'item: {subval}')
            print(f'{k}: {v}')



    return config

def process_list():
    for proc in psutil.process_iter():
        try:
            # Get process name & pid from process object.
            processName = proc.name()
            processID = proc.pid
            print(processName, ' ::: ', processID)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass


def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False;

def poll_process_list(config):
    for sec in config.sections():
        print(sec)
        for k,v in config[sec].items():
            if k == 'item':
                subval = v.split()
                for val in subval:
                    res = checkIfProcessRunning(val)
                    print(f'{val} is running {res}')





# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    make_default_ini()
    conf = read_ini()
    print(conf.sections())
    process_list()
    poll_process_list(conf)

    im= InhitorManager()
    print('adding')
    im.inhibit('chump',EVENTS['SUSPEND'])

    import time
    time.sleep(10)
    print('remove')
    im.remove('chump')
    time.sleep(10)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
