"""
Script using the Windows API to register for window focus changes and print the
titles of newly focused windows.
"""
#https://github.com/Danesprite/windows-fun/blob/master/window%20change%20listener.py
import sys
import time
import ctypes
import ctypes.wintypes
import threading
import six
import win32gui


class ObservableWindowChange(object):
    def __init__(self):
        self.__observers = []

    def register_observer(self, observer):
        self.__observers.append(observer)

    def notify_observers(self, *args, **kwargs):
        win_title = ''.join(args)
        if win_title == '':
            return ''
        for observer in self.__observers:
            observer.notify(win_title)

    def start_event_listener(self):
        # Create a WindowChangeEventListener object with this instance of
        # ObservableWindowChange as a parameter (self)
        listener = WindowChangeEventListener(self)
        listener.listen_forever()


class IWindowChangeObserver(object):
    """
    Base class for observing window changes
    """
    def __init__(self, observable, interface=None):
        observable.register_observer(self)
        self.interface = interface

    def notify(self, win_title):
        raise NotImplementedError


class WindowChangeEventListener(object):
    """
    WindowChangeEventListener
    """
    def __init__(self, observable):
        self.observable = observable

    def listen_forever(self):        
        # This is to fix a problem with ascii encoding (windows with Unicode in
        # their titles)
        if six.PY2:
            reload(sys)
            sys.setdefaultencoding('utf8')

        # Look here for DWORD event constants:
        # http://stackoverflow.com/questions/15927262/convert-dword-event-constant-from-wineventproc-to-name-in-c-sharp
        # Don't worry, they work for python too.
        EVENT_SYSTEM_DIALOGSTART = 0x0010
        WINEVENT_OUTOFCONTEXT = 0x0000
        EVENT_SYSTEM_FOREGROUND = 0x0003
        WINEVENT_SKIPOWNPROCESS = 0x0002

        user32 = ctypes.windll.user32
        ole32 = ctypes.windll.ole32
        EnumWindows = ctypes.windll.user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool,
                                             ctypes.POINTER(ctypes.c_int),
                                             ctypes.POINTER(ctypes.c_int))
        GetWindowText = ctypes.windll.user32.GetWindowTextW
        GetForegroundWindow = ctypes.windll.user32.GetForegroundWindow
        GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
        IsWindowVisible = ctypes.windll.user32.IsWindowVisible

        ole32.CoInitialize(0)

        WinEventProcType = ctypes.WINFUNCTYPE(
            None,
            ctypes.wintypes.HANDLE,
            ctypes.wintypes.DWORD,
            ctypes.wintypes.HWND,
            ctypes.wintypes.LONG,
            ctypes.wintypes.LONG,
            ctypes.wintypes.DWORD,
            ctypes.wintypes.DWORD
        )

        def callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread,
                     dwmsEventTime):
            length = GetWindowTextLength(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buff, length + 1)
            # hwnd = GetForegroundWindow()
            # Notify observers
            self.observable.notify_observers(buff.value)
            

        WinEventProc = WinEventProcType(callback)

        user32.SetWinEventHook.restype = ctypes.wintypes.HANDLE
        hook = user32.SetWinEventHook(
            EVENT_SYSTEM_FOREGROUND,
            EVENT_SYSTEM_FOREGROUND,
            0,
            WinEventProc,
            0,
            0,
            WINEVENT_OUTOFCONTEXT | WINEVENT_SKIPOWNPROCESS
        )
        if hook == 0:
            print('SetWinEventHook failed')
            exit(1)

        msg = ctypes.wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
            user32.TranslateMessageW(msg)
            user32.DispatchMessageW(msg)

        # Stopped receiving events, so clear up the winevent hook and uninitialise.
        print('Stopped receiving new window change events. Exiting...')
        user32.UnhookWinEvent(hook)
        ole32.CoUninitialize()


class WindowObserver(IWindowChangeObserver):
    def notify(self, win_text):
        time.sleep(0.3)
        win_hwnd = win32gui.GetForegroundWindow()
        # print("Window '%s' focused" % win_text)
        if self.interface:
            self.interface.update_perso_and_visibility(win_hwnd)


def run(interface=None):
    # Create an observable and an observer observing it
    subject = ObservableWindowChange()
    observer = WindowObserver(subject, interface=interface)

    # Listen for window changes
    subject.start_event_listener()

class ThreadListener(threading.Thread):
    def __init__(self, interface=None):
        threading.Thread.__init__(self)
        self.interface = interface
        self.start()
        
    def run(self):
        run(self.interface)
        
    def kill(self):
        print("kill")


if __name__ == '__main__':

    

    # Start the 'run' method in a daemonized thread.
    # t = threading.Thread(target=run)
    # t.setDaemon(True)
    # t.start()
    
    t = ThreadListener(None)

    # Keep the main thread running in a sleep loop until ctrl+c (SIGINT) is caught.
    # Once the main thread terminates, all daemon threads will automatically
    # terminate.
    cpt=0
    while True:
        try:
            time.sleep(0.1)
            cpt+=1
            if cpt>10:
                t.kill()
        except KeyboardInterrupt:
            break