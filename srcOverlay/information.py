import json
import logging  

path = "ressources/information.json"

class Information:
    
    with open(path, "r",encoding='utf-8') as f:
        information = json.load(f)
    
    @classmethod
    def loadInfo(self):
        with open(path, "r",encoding='utf-8') as f:
            self.information = json.load(f)
    
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
            if "classe" in self.information[dofus.name]:
                dofus.classe = self.information[dofus.name]["classe"]
            if "sexe" in self.information[dofus.name]:
                dofus.sexe = self.information[dofus.name]["sexe"]
            if "ini" in self.information[dofus.name]:
                dofus.ini = int(self.information[dofus.name]["ini"])
            if "type" in self.information[dofus.name]:
                dofus.type = self.information[dofus.name]["type"]
            if "head" in self.information[dofus.name]:
                dofus.head = self.information[dofus.name]["head"]
            if "image_path" in self.information[dofus.name]:
                dofus.image_path = self.information[dofus.name]["image_path"]
            

    
    @classmethod   
    def getAllSavedName(self):
        return list(self.information.keys())
            
            