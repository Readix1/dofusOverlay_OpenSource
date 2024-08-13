import win32gui
from threading import Thread, Lock
import time
import win32process
import psutil

start_time = time.time()
from srcOverlay.Page_Dofus import Page_Dofus
print("fin import Page_Dofus --- %s seconds ---" % (time.time() - start_time))

from srcOverlay.Observer import Observer
import logging
from srcOverlay.initiative import Initiative 


INI = "D:\\all\\bot\\python\\pythondof\\dofusOverlay\\ressources\\res_dofus\\initiative.json"


class DofusHandler(Thread,Observer):
    """
    Class qui gere les id des fenetres dofus (hwnd) et leur ordre
    
    event : update_hwnd
    """
    def __init__(self):
        Thread.__init__(self)
        Observer.__init__(self,["update_hwnd", "update_selected_perso", "getHwnd", 'shutdown', "get_selected_pages"])  
        self.curr_hwnd = 0
        self.running = True
        self.dofus = sorted([Page_Dofus(hwnd, self) for hwnd in self._get_win()], key=lambda x: x.ini, reverse=True)

        self.dofusDict = {d.hwnd:d for d in self.dofus}
        self.lock = Lock()
        self.name_order = []
        self.cover=[]
    
        
        
    def get_hwnds(self):
        return [d.hwnd for d in self.dofus]

    def get_hwnds_order(self):
        hwnds = self.get_hwnds()
        return sorted(hwnds, key=lambda x: self.dofusDict[x].ini, reverse=True)
    
    def get_names_order(self):
        return [self.dofusDict[h].name for h in self.get_hwnds_order()]
    
    def is_dofus_window(self,hwnd):
        return hwnd in self.get_hwnds()

    def get_pids(self):
        return [d.pid for d in self.dofus]
    
    def get_names(self):
        return [d.name for d in self.dofus]
    

    def stop(self):
        self.running = False
        
    def _get_win(self):
        tmp = []
        win32gui.EnumWindows(dofusEnumerationHandler, tmp)
        return tmp
    
    # def append_dofus_and_sort(self,dofus):
    #     for d in dofus:
    #         if d not in self.dofus:
    #             self.dofus.append(d)
    #     self.dofus = sorted(self.dofus, key=lambda x: x.ini, reverse=True)
    
    def add_win(self,hwnd):
        self.lock.acquire()
        
        if hwnd not in self.get_hwnds():
            d = Page_Dofus(hwnd, self)
            self.dofus.append(d)
            self.dofusDict[hwnd]=d
            self.lock.release()
            self.notify("update_hwnd", self.get_hwnds(), self.get_names())
            return True
        
        self.lock.release()
        return False
        
    def is_dofus_window(self,hwnd):
        hwnds = self.notify("getHwnd")
        hwnds = [] if hwnds == None else hwnds
        return hwnd in self.get_hwnds()+ hwnds
    
    def get_hwnd_by_name(self,name):
        namelist = self.get_names()
        return self.dofus[namelist.index(name)].hwnd
    
    def get_dofus_by_name(self,name):
        namelist = self.get_names()
        namelist = [n.lower() for n in namelist]
        return self.dofus[namelist.index(name)]
        
    def get_index_by_hwnd(self, hwnd):
        return self.get_hwnds().index(hwnd)

    def next_element(self, list_, hwnd):
        i = list_.index(hwnd)
        return list_[(i+1) % len(list_)]
    
    def previous_element(self, list_, hwnd):
        i = list_.index(hwnd)
        return list_[(i-1) % len(list_)]
    
    def get_next_hwnd(self, hwnd):
        selected = self.notify("get_selected_pages")
        if len(selected) == 0 or hwnd not in selected:
            return self.next_element(self.get_hwnds(), hwnd)
        
        return self.next_element([h for h in self.get_hwnds() if h in selected], hwnd)
        
    def get_previous_hwnd(self, hwnd):
        selected = self.notify("get_selected_pages")
        if len(selected) == 0 or hwnd not in selected:
            return self.previous_element(self.get_hwnds(), hwnd)
        
        return self.previous_element([h for h in self.get_hwnds() if h in selected], hwnd)
    
    def get_next_dofus(self):
        curr = self.get_curr_hwnd()
        if not curr in self.get_hwnds():
            curr=self.curr_hwnd if self.curr_hwnd in self.get_hwnds() else self.get_hwnds()[0]
        next_hwnd = self.get_next_hwnd(curr)
        self.notify("update_selected_perso",next_hwnd)
        return self.dofusDict[next_hwnd]
    
    def get_previous_dofus(self):
        curr = self.get_curr_hwnd()
        if not curr in self.get_hwnds():
            curr=self.curr_hwnd if self.curr_hwnd in self.get_hwnds() else self.get_hwnds()[0]
        previous_hwnd = self.get_previous_hwnd(curr)
        self.notify("update_selected_perso",previous_hwnd)
        return self.dofusDict[previous_hwnd]
    
    def get_current_dofus(self):
        """ renvoie le dofus qui est affiché sur l'écran sinon renvoie le premier de la liste"""
        curr = self.get_curr_hwnd()
        if not curr in self.get_hwnds():
            curr=self.curr_hwnd if self.curr_hwnd in self.get_hwnds() else self.get_hwnds()[0]
        i = self.get_index_by_hwnd(curr)
        self.notify("update_selected_perso",self.dofus[i].hwnd)
        return self.dofus[i]
    
    def get_curr_hwnd(self):
        """ renvoie le hwnd de la fenetre qui est au premier plan"""
        tmp = win32gui.GetForegroundWindow()
        if(self.is_dofus_window(tmp)):
            self.curr_hwnd = tmp
        return self.curr_hwnd
    
    def __len__(self):
        return len(self.dofus)
    
    def remove_win(self,hwnd):
        self.lock.acquire()
        i = self.get_index_by_hwnd(hwnd)
        self.dofus.pop(i)
        del self.dofusDict[hwnd]
        self.lock.release()
        self.notify("update_hwnd",self.get_hwnds(),self.get_names())
    
    def run(self):
        while self.running :
            hwnd_tmp = self._get_win()
            
            #test si les fenetres ont été fermées
            for hwnd in self.get_hwnds():
                if hwnd not in hwnd_tmp:
                    self.remove_win(hwnd)
                    
            #test si des fenetres ont été ouvertes
            for hwnd in hwnd_tmp:
                self.add_win(hwnd)
            
            up = False
            for d in self.dofus:
                if d.update_name():
                    self.dofus=sorted(self.dofus, key=lambda x: x.ini, reverse=True)
                    up =True
            if(up):
                logging.info(f"dofus window name updated {self.get_names()}")
                self.notify("update_hwnd",self.get_hwnds_order(),self.get_names_order())
            
            tmp_name_order = self.get_names()
            if(tmp_name_order != self.name_order):
                self.notify("update_hwnd",self.get_hwnds_order(),self.get_names_order())
                self.name_order = self.get_names()

            time.sleep(0.3)
        logging.info("dofus window handler stopped")
            
            
def dofusEnumerationHandler(hwnd, top_windows):
    name = win32gui.GetWindowText(hwnd)
    _,pid = win32process.GetWindowThreadProcessId(hwnd)
    try:
        exe = psutil.Process(pid).exe()
        visible = win32gui.IsWindowVisible(hwnd)
        if("dofus 2" in name.lower() and "dofus.exe" in exe.lower() and visible):
            top_windows.append(hwnd)
    except psutil.NoSuchProcess:
        pass
    except ValueError:
        pass
        
        
if __name__ == "__main__":
    dh = DofusHandler()
    dh.start()