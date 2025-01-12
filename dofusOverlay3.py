import time

start_time = time.time()
from srcOverlay.dofushandler import DofusHandler
from srcOverlay.listener import Listener
from srcOverlay.dofusmanager import DofusManager
from srcOverlay.interface.dofus_overlay import DofusOverlay
from srcOverlay.interface.dofusGuide_overlay import DofusGuideOverlay
import logging
import json 
import argparse
import sys
print("fin import --- %s seconds ---" % (time.time() - start_time))


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
if config["overlay"]["auto-actualisation"]:
    dh.start()
dm = DofusManager(config, dh)

if config["overlay"]["afficher_overlay"]:
    interface = DofusGuideOverlay(config, dh.dofus, dh.open_index_dofus, dh=dh, head_width=config["overlay"]["icon_width"], orientation=config["overlay"]["horizontal"])
    if config["overlay"]["auto-actualisation"]:
        Listener(dh).start()
    # ThreadListener(interface)

    dh.add_observer("reorganise", lambda dofus: interface.ask_open_reorganize(dofus))
    dh.add_observer("update_shortcut", lambda shortcut_name, shortcut, specific: dm.update_shortcut(shortcut_name, shortcut, specific))
    dh.add_observer("get_shortcut", lambda : dm.get_shortcut())
    
    
    dh.add_observer("save_button", lambda : dm.save_config())
    dh.add_observer("stop",interface.stop)
    dh.add_observer("stop",dm.stop_manager)
    dh.add_observer("update_shown_page",lambda indice: interface.update_perso(indice))
    if config["overlay"]["auto-disparition"]:
        dh.add_observer("update_visible",lambda hwnd: interface.update_visibility(hwnd))
    dh.add_observer("update_order",lambda order : interface.update_order(order))
    dh.add_observer('getHwnd',lambda : interface.getHwnd())
    
    interface.mainloop()


if config["overlay"]["auto-actualisation"]:
    dh.join()
else:
    dm.listener.join()