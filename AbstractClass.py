# Importujemy moduł abc (Abstract Base Classes)
from abc import ABC, abstractmethod

from sympy.physics.units import length


#definiujemy klasę abstrakcyjną Shape dziedziczącą po ABC

class Base(ABC):
    # Definiujemy metodę abstrakycjną area, którą muszą implementować klasy dziedziczące
    @abstractmethod
    def area(self):
        pass

    # Definiujemy inną metodę abstrakcyjną perimeter
    @abstractmethod
    def perimeter(self):
        pass


class Rectangle(Base):
    def __init__(self, lenght, width):
        #Przypisanie atrybutów instancji
        self.lenght = lenght
        self.width = width

    #Implementujemy wymaganą metodę area
    def area(self):
        #zwracamy pp
        return self.lenght * self.width

    def perimeter(self):
        #zwracamy obw
        return 2*(self.lenght+self.width)

rect = Rectangle(4,5)
print("Pole prostokąta:", rect.area())
print("Obwód prostokąta:",rect.perimeter())