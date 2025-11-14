from abc import ABC, abstractmethod
class Entity(ABC):
    def __init__(self, position: tuple[int,  int]):
        self._position=position

    @abstractmethod
    def symbol(self):
        return self._position

class Damageably(ABC):
    def __init__(self, health: float, max_health: float):
        self._health=health
        self._max_health = max_health
    
    def isalive(self):
        if self._health>0:
            return True
        else:
            return False
        
    def heal(self, amount: float):
        if self._max_health-self._health<amount:
            self._health=self._max_health
        else:
            self._health+=amount
        return self._health

    def take_damage(self, amount: float):
        self._health-=amount
        if self.isalive():
            return self._health
        else:
            return "DEATH"
        
    
class Attacker(ABC):
    @abstractmethod
    def attack(self, target: Damageably):
        damage=float(input())
        return damage

class Bonus(ABC, Entity):
    """Абстракция всех бонусов"""

    def __init__(self, player: "Player"):
        player+=self


class Player():
    """игрок"""
    def __init__(self, max_health: int, damage: int, coins: int):
        self.__health=max_health
        self.max_health=max_health
        self.damage=damage
        self.__coords=[0,0]
        self.coins=coins
        self.medkits=[]
        self.furies=[]
    
gggg=Bonus()