import time
import logging
from threading import Thread, Lock

import win32gui
import win32process
import psutil

from srcOverlay.Page_Dofus import Page_Dofus
from srcOverlay.Observer import Observer
from srcOverlay.information import Information

from bisect import insort

class DofusHandler(Thread,Observer):
    """
    Class qui gere les id des fenetres dofus (hwnd) et leur ordre
    
    event : update_order
    """
    def __init__(self):
        Thread.__init__(self)
        Observer.__init__(self,["update_order", "getHwnd", "reorganise", "update_shortcut", "save_button", "get_shortcut",
                                "update_shown_page", "update_visible", "stop"])  
        self.running = True
        
        self.dofus = sorted([Page_Dofus(hwnd, self) for hwnd in self._get_win()], key=lambda x: x.ini, reverse=True)
        
        self.curr_hwnd = 0
        self.current_shown = 0
        
        self.lock = Lock()
        self.name_order = []
        
        self.actualise()
        
    def update_shortcut(self, shortcut_name, shortcut, specific=False):
        self.notify("update_shortcut", shortcut_name, shortcut, specific)
        
    def get_shortcut(self):
        return self.notify("get_shortcut")
        
    def open_reorganize(self):
        self.notify("reorganise", self.dofus)
        
    def update_shown(self, hwnd):
        if hwnd in self.get_hwnds():
            self.curr_hwnd = hwnd
            self.current_shown = self.get_index_by_hwnd(hwnd)
            self.notify('update_shown_page', self.current_shown)
        
        self.notify('update_visible', hwnd)
    
    def save_dofus_info(self):
        Information.saveMultipleInfo(self.dofus)
        self.notify("save_button")
        
    def load_dofus_info(self):
        Information.loadInfo()
        for d in self.dofus:
            d.get_info()
        
    def get_selected_pages(self):
        return [i for i, d in enumerate(self.dofus) if d.selected]
    
    def open_specific_page(self, name):
        for i, d in enumerate(self.dofus):
            if d.name == name:
                self.open_index_dofus(i)
                return

    def open_next_page(self):
        selected = self.get_selected_pages()
        if len(selected) == 0:
            self.open_index_dofus((self.current_shown+1)%len(self.dofus))
            return
        
        index = (self.current_shown+1)%len(self.dofus)
        while index not in selected:
            index = (index+1)%len(self.dofus)
        
        self.open_index_dofus(index)
        
    def click_current_page(self):
        self.dofus[self.current_shown].click()
        
    def open_previous_page(self):
        selected = self.get_selected_pages()
        if len(selected) == 0:
            self.open_index_dofus((self.current_shown-1)%len(self.dofus))
            return
        
        index = (self.current_shown-1)%len(self.dofus)
        while index not in selected:
            index = (index-1)%len(self.dofus)
        
        self.open_index_dofus(index)

    def open_current_page(self):
        self.open_index_dofus(self.current_shown)
    
    def open_index_dofus(self, index):
        self.current_shown = index
        self.notify('update_shown_page', self.current_shown)
        self.dofus[self.current_shown].open()
        
    def get_hwnds(self):
        return [d.hwnd for d in self.dofus]
    
    def get_index_by_hwnd(self, hwnd):
        return self.get_hwnds().index(hwnd)       
    
    def update_order(self):
        if self.dofus:
            current_dofus = self.dofus[self.current_shown] if self.current_shown < len(self.dofus) else self.dofus[-1]
            # self.dofus=sorted(self.dofus, key=lambda x: x.ini, reverse=True)
            self.dofus.sort(key=lambda x: x.ini, reverse=True)
            self.current_shown = self.dofus.index(current_dofus)
            self.notify("update_shown_page", self.current_shown)
        self.notify("update_order", self.dofus)
        
    def get_names(self):
        return [d.name for d in self.dofus]
    
    def is_dofus_window(self,hwnd):
        hwnds = self.notify("getHwnd")
        hwnds = [] if hwnds == None else hwnds
        return hwnd in self.get_hwnds()+ hwnds
    
    def remove_win(self,hwnd):
        with self.lock:
            i = self.get_index_by_hwnd(hwnd)
            self.dofus.pop(i)
        self.notify("update_order", self.dofus)
        
    def stop(self):
        self.notify('stop')
        self.running = False
        
    def _get_win(self):
        top_windows = []
        process_cache = {}  # Cache pour mémoriser les informations de processus
        def enumeration_callback(hwnd, _):
            dofusEnumerationHandler(hwnd, top_windows, process_cache)

        win32gui.EnumWindows(enumeration_callback, None)
        return top_windows

    
    def add_win(self,hwnd):
        with self.lock:
            if hwnd not in self.get_hwnds():
                page = Page_Dofus(hwnd, self)
                self.dofus.append(page)
                self.notify("update_order", self.dofus)
                return True
        return False
        
    def actualise(self):
        # Collecte des fenêtres visibles
        current_hwnds = set(self._get_win())

        # Mise à jour des fenêtres existantes
        existing_hwnds = set(self.get_hwnds())
        closed_hwnds = existing_hwnds - current_hwnds
        new_hwnds = current_hwnds - existing_hwnds

        # Supprimer les fenêtres fermées
        for hwnd in closed_hwnds:
            self.remove_win(hwnd)

        # Ajouter les nouvelles fenêtres
        for hwnd in new_hwnds:
            self.add_win(hwnd)

        # Vérifiez si des noms ont changé
        name_updated = any(page.update_name() for page in self.dofus)
        if name_updated:
            logging.info(f"Dofus window names updated: {self.get_names()}")
            self.update_order()

        
        # tmp_name_order = self.get_names()
        # if(tmp_name_order != self.name_order):
        #     self.notify("update_order", self.dofus)
        #     self.name_order = self.get_names()
        
    
    def run(self):
        while self.running :
            self.actualise()

            time.sleep(0.3)
        logging.info("dofus window handler stopped")
            
            
def dofusEnumerationHandler(hwnd, top_windows, process_cache):
    # Vérifier si la fenêtre est visible
    if not win32gui.IsWindowVisible(hwnd):
        return

    # Obtenir le PID du processus associé à la fenêtre
    _, pid = win32process.GetWindowThreadProcessId(hwnd)

    # Éviter les doublons et appels répétitifs avec un cache
    if pid not in process_cache:
        try:
            # Récupérer l'exécutable associé au processus
            exe = psutil.Process(pid).exe().lower()
            process_cache[pid] = "dofus.exe" in exe
        except (psutil.NoSuchProcess, ValueError):
            process_cache[pid] = False


    # Si c'est le bon processus, ajouter la fenêtre à la liste
    if process_cache[pid]:
        top_windows.append(hwnd)
        
        
if __name__ == "__main__":
    dh = DofusHandler()
    dh.start()