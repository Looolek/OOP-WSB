from abc import ABC, abstractmethod

class Balwan(ABC):

    @abstractmethod
    def tworzbalw(self):
        pass

    @abstractmethod
    def elimbalw(self):
        pass

class CyrkNaKolkach(Balwan):

    def tworzbalw(self):
        return "Balwan powstal"

    def elimbalw(self):
        return "Balwan umarl"

class Cyrk(CyrkNaKolkach):
    pass

czlowiek = Cyrk()

print(czlowiek.tworzbalw())
print(czlowiek.elimbalw())
