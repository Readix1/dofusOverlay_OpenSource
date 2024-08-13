import json
import logging  

class Initiative:
    
    with open("ressources/initiative.json", "r",encoding='utf-8') as f:
        initiative = json.load(f)
        
    @classmethod   
    def updateIni(self, ini, nom):
        self.initiative[nom]=ini
        self.saveIni()
        
    @classmethod   
    def saveIni(self):
        with open('ressources/initiative.json', 'w') as fp:
            json.dump(self.initiative, fp, indent=4)
            
    @classmethod   
    def getIni(self, name):
        if name in self.initiative:
            return self.initiative[name]
        else:
            return 0
    
    @classmethod   
    def getAllInitiativeName(self):
        return list(self.initiative.keys())
            
            