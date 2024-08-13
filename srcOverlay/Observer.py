
class Observer:
    def __init__(self,events_name):
        self.observers = {event_type : [] for event_type in events_name}
        
    def add_observer(self,event_type,callback):
        if(event_type in self.observers):
            self.observers[event_type].append(callback)
        else:
            raise RuntimeError("Event type not found :",event_type,"in",self.__name__)
        
    def remove_observer(self,event_type,callback):
        if(event_type in self.observers):
            self.observers[event_type].remove(callback)
        else:
            raise RuntimeError("Event type not found :",event_type,"in",self.__name__)
        
    def notify(self,event_type,*args):
        res=None
        for f in self.observers[event_type]:
            res=f(*args)
        return res