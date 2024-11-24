import json
import logging  

path = "ressources/information.json"

class Information:
    
    with open(path, "r",encoding='utf-8') as f:
        information = json.load(f)
        
    @classmethod   
    def updateInfo(self, dofus):
        res = dofus.serialize()
        if res != {}:
            self.information.update(res)
            self.saveInfo()
    
    @classmethod
    def saveMultipleInfo(self, dofus_list):
        for dofus in dofus_list:
            res = dofus.serialize()
            if res != {}:
                self.information.update(res)
        self.saveInfo()
        
    @classmethod   
    def saveInfo(self):
        with open(path, 'w') as fp:
            json.dump(self.information, fp, indent=4)
            
    @classmethod   
    def getInfo(self, dofus):
        if dofus.name in self.information:
            dofus.classe = self.information[dofus.name]["classe"]
            dofus.sexe = self.information[dofus.name]["sexe"]
            dofus.ini = int(self.information[dofus.name]["ini"])
            

    
    @classmethod   
    def getAllSavedName(self):
        return list(self.information.keys())
            
            