import time

start_time = time.time()
from srcOverlay.dofushandler import DofusHandler
print("fin import DofusHandler --- %s seconds ---" % (time.time() - start_time))
# print("fin import DofusHandler")
from srcOverlay.listener import Listener
from srcOverlay.dofusmanager import DofusManager
from srcOverlay.interface.dofus_overlay import DofusOverlay
import logging
import json 
import argparse
import sys

DEFAULT_LEVEL_LOGGING = logging.INFO

parser = argparse.ArgumentParser()
parser.add_argument('--nodebug', action='store_false')
args = parser.parse_args()

if(args.nodebug):
    logging.basicConfig(level=logging.INFO)
    logging.basicConfig(level=DEFAULT_LEVEL_LOGGING, format='[%(levelname)s] (%(threadName)-9s) %(message)s')
else:
    logging.basicConfig(level=logging.WARNING, format='[%(levelname)s] (%(threadName)-9s) %(message)s')


with open("ressources/config.json",encoding="utf-8") as file:
    config = json.load(file)

dh = DofusHandler()
dh.start()
dm = DofusManager(config,dh)

dm.add_observer("stop",dh.stop)

if config["overlay"]["actif"]:
    interface = DofusOverlay(config, dh.get_hwnds_order(), dh.get_names_order(), dm._open_dofus, dh=dh)
    Listener(dm, interface).start()
    # ThreadListener(interface)

    dm.add_observer("stop",interface.stop)
    dm.add_observer("switch_page",lambda hwnd: interface.update_perso_and_visibility(hwnd))
    dm.add_observer("reorganise", lambda : interface.open_reorganize(dh.get_hwnds_order(), dh.get_names_order()))

    dh.add_observer("update_hwnd",lambda order,order_name : interface.update_order(order,order_name))
    dh.add_observer("update_selected_perso",lambda hwnd : interface.update_perso(hwnd))
    dh.add_observer('getHwnd',lambda : interface.getHwnd())
    dh.add_observer('get_selected_pages',lambda : interface.get_selected_pages())

    interface.mainloop()
dh.join()