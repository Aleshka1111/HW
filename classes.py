from abc import ABC, abstractmethod
from random import randint, random, choice


CLASS_REGISTRY = {}

def register_class(cls):
    CLASS_REGISTRY[cls.__name__] = cls
    return cls

class Entity(ABC):

    def __init__(self, position: tuple[int, int]):
        self._position = position

    @property
    def position(self):
        return self._position

    @abstractmethod
    def symbol(self):
        pass


class Damageable(ABC):

    def __init__(self, hp: float, max_hp: float):
        self._hp = hp
        self._max_hp = max_hp

    def is_alive(self):
        return self._hp > 0

    def heal(self, amount: float):
        regen = min(amount, self._max_hp - self._hp)
        self._hp += regen
        return regen

    def take_damage(self, amount: float):
        damage = min(amount, self._hp)
        self._hp -= damage
        return damage


class Attacker(ABC):

    @abstractmethod
    def attack(self, target: Damageable):
        pass

class Weapon(Entity):

    def __init__(self, name: str, max_damage: float, position: tuple[int, int]):
        Entity.__init__(self, position)
        self._name = name
        self._max_damage = max_damage

    @abstractmethod
    def roll_damage(self):
        pass

    def is_available(self):
        return True

    def symbol(self):
        return "W"
    

class MeleeWeapon(Weapon):

    def damage(self, rage: float):
        return self.roll_damage() * rage
    
    def to_dict(self):

        return {
            "type": "melee",
            "name": self._name,
            "max_damage": self._max_damage,
            "position": self.position,
            "available": self.is_available(),
            "durability": getattr(self, '_durability', None)  
        }
    

class RangedWeapon(Weapon):
    
    def __init__(self, name:str, max_damage: float, ammo: int, position: tuple):
        super().__init__(name, max_damage, position)
        self._ammo = ammo
        self._ammo_consumption = 1 if name == "Лук" else 2

    def consume_ammo(self, n=1):
        if self._ammo >= n:
            self._ammo -= n
            return True
        return False

    def is_available(self):
        return self._ammo > 0

    def damage(self, accuracy: float):
        if self.consume_ammo(self._ammo_consumption):
            return self.roll_damage() * accuracy
        return 0.0
    
    def to_dict(self):
        return {
            "type": "ranged",
            "name": self._name,
            "max_damage": self._max_damage,
            "position": self.position,
            "available": self.is_available(),
            "ammo": self._ammo,
            "ammo_consumption": self._ammo_consumption
        }


class Fist(MeleeWeapon):

    def __init__(self, position: tuple[int, int]):
        super().__init__(name="Кулак", max_damage=20, position=position)

    def roll_damage(self):
        return randint(0,int(self._max_damage))


    def damage(self, rage:float):
        return self.roll_damage()*rage
    
    @classmethod
    def from_dict(cls, data):
        instance = cls(position=tuple(data["position"]))
        return instance

CLASS_REGISTRY["Fist"] = Fist


class Stick(MeleeWeapon):

    def __init__(self, position: tuple[int, int]):
        super().__init__(name="Палка", max_damage = 25, position=position)
        self._durability = randint(10, 20)

    def is_available(self):
        return self._durability > 0

    def roll_damage(self):
        return randint(0, int(self._max_damage))


    def damage(self, rage: float):
        if self._durability > 0:
            self._durability -= 1
            return self.roll_damage() * rage
        return 0.0

    @classmethod
    def from_dict(cls, data):
        instance = cls(position=tuple(data["position"]))
        instance._durability = data["durability"]
        return instance

CLASS_REGISTRY["Stick"] = Stick


class Bow(RangedWeapon):


    def __init__(self, position):
        ammo = randint(10, 15)
        super().__init__(name = "Лук", max_damage = 35, ammo = ammo, position = position)

    def roll_damage(self):
        return randint(0, int(self._max_damage))
    
    @classmethod
    def from_dict(cls, data):
        instance = cls(position=tuple(data["position"]))
        instance._ammo = data["ammo"]
        return instance

CLASS_REGISTRY["Bow"] = Bow

class Revolver(RangedWeapon):

    def __init__(self, position: tuple[int, int]):
        ammo = randint(5, 10)
        super().__init__(name = "Револьвер", max_damage= 45, ammo=ammo, position=position)

    def roll_damage(self):
        return randint(0, int(self._max_damage))
    
    @classmethod
    def from_dict(cls, data):
        instance = cls(position=tuple(data["position"]))
        instance._ammo = data["ammo"]
        return instance

    @classmethod
    def from_dict(cls, data):
        instance = cls(position=tuple(data["position"]))
        instance._ammo = data["ammo"]
        return instance

CLASS_REGISTRY["Revolver"]=Revolver



class Bonus(Entity):


    def __init__(self, position: tuple[int, int]):
        super().__init__(position)

    @abstractmethod
    def apply(self,player):
        pass

    def symbol(self):
        return "B"


class Medkit(Bonus):

    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self._power =randint(10, 40)

    def apply(self, player: 'Player'):
        if player.fight:
            healed = player.heal(self._power)
            print(f"+{healed} HP от аптечки")
        else:
            player.add_to_inventory("Medkit", self)

    def to_dict(self):
        return{
            "class": "medkit",
            "position": self.position,
            "power": self._power
        }
    
    @classmethod
    def from_dict(cls, data):
        instance = cls(position=tuple(data["position"]))
        instance._power = data["power"]
        return instance

CLASS_REGISTRY["medkit"] = Medkit


class Rage(Bonus):

    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self._multiplier = 1.0 + random()

    def apply(self, player: 'Player'):
        if player.fight:
            player._rage += self._multiplier
            print(f"Ярость увеличена на {self._multiplier:.1f}")
        else:
            player.add_to_inventory("Rage", self)

    def to_dict(self):
        return{
            "class": "rage",
            "position": self.position,
            "multiplayer": self._multiplier
        }

    @classmethod
    def from_dict(cls, data):
        instance = cls(position=tuple(data["position"]))
        instance._multiplier = data["multiplayer"]  
        return instance

CLASS_REGISTRY["rage"] = Rage


class Arrows(Bonus):

    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self._amount = randint(1, 20)

    def apply(self, player: 'Player'):
        if isinstance(player._weapon, Bow):
            player._weapon._ammo += self._amount
            print(f"+{self._amount} стрел")
        else:
            player.add_to_inventory("Arrows", self)

    def to_dict(self):
        return{
            "class": "arrows",
            "position": self.position,
            "amount": self._amount
        }
    
    @classmethod
    def from_dict(cls, data):
        instance = cls(position=tuple(data["position"]))
        instance._amount = data["amount"]
        return instance

CLASS_REGISTRY["arrows"] = Arrows



class Bullets(Bonus):

    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self._amount = randint(1, 10)

    def apply(self, player: 'Player'):
        if isinstance(player._weapon, Revolver):
            player._weapon._ammo += self._amount
            print(f"+{self._amount} патронов")
        else:
            player.add_to_inventory("Bullets", self)

    def to_dict(self):
        return{
            "class": "bullets",
            "position": self.position,
            "amount": self._amount
        }
    
    @classmethod
    def from_dict(cls, data):
        instance = cls(position=tuple(data["position"]))
        instance._amount = data["amount"]
        return instance

CLASS_REGISTRY["bullets"] = Bullets

class Accuracy(Bonus):

    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self._multiplier = 0.1 + random() * 0.9

    def apply(self, player: 'Player'):
        if player.fight:
            player._accuracy += self._multiplier
            print(f"Точность увеличена на {self._multiplier:.1f}")
        else:
            player.add_to_inventory("Accuracy", self)

    def to_dict(self):
        return{
            "class": "accuracy",
            "position": self.position,
            "multiplier": self._multiplier
        }

    @classmethod
    def from_dict(cls, data):
        instance = cls(position=tuple(data["position"]))
        instance._multiplier = data["multiplier"]
        return instance

CLASS_REGISTRY["accuracy"] = Accuracy



class Coins(Bonus):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self._amount = randint(50, 100)

    def apply(self, player:'Player'):
        player.add_coins(self._amount)
        print(f"+{self._amount} монет")

    def to_dict(self):
        return{
            "class": "coins",
            "position": self.position,
            "amount": self._amount
        }
    
    @classmethod
    def from_dict(cls, data):
        instance = cls(position=tuple(data["position"]))
        instance._amount = data["amount"]
        return instance

CLASS_REGISTRY["coins"] = Coins

class Structure(Entity):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position )

    @abstractmethod
    def interact(self, player: 'Player', board: 'Board'):
        pass

    def symbol(self):
        return "T"


class Tower(Structure):

    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self._reveal_radius = 2

    def interact(self, board: 'Board'):
        r, c = self._position
        for dr in range(-self._reveal_radius, self._reveal_radius + 1):
            for dc in range(-self._reveal_radius, self._reveal_radius + 1):
                nr, nc = r + dr, c + dc
                if board.in_bounds((nr, nc)):
                    board.reveal((nr, nc))
        print("Башня открыла окрестности!")

    def to_dict(self):
        return{
            "class": "tower",
            "position": self.position
        }
    
    @classmethod
    def from_dict(cls, data):
        instance = cls(position=tuple(data["position"]))
        return instance

CLASS_REGISTRY["tower"] = Tower

class Enemy(Entity, Damageable, Attacker):

    def __init__(self, lvl: int, max_hp: float, max_damage: float, reward_coins: int, position: tuple[int, int]):
        Entity.__init__(self, position)
        Damageable.__init__(self, hp=max_hp, max_hp=max_hp)
        self._lvl = lvl
        self._max_enemy_damage = max_damage
        self._reward_coins = reward_coins

    def roll_enemy_damage(self):
        return randint(0, int(self._max_enemy_damage))

    def attack(self, target: 'Player'):
        dmg = self.roll_enemy_damage()
        target.take_damage(dmg)
        return dmg

    @abstractmethod
    def before_turn(self, player: 'Player'):
        pass

    def symbol(self):
        return "E"


class Rat(Enemy):

    def __init__(self, lvl: int, position: tuple[int, int]):
        hp = 100 * (1 + lvl / 10)
        max_dmg = 15 * (1 + lvl / 10)
        super().__init__(lvl, hp, max_dmg, 200, position)
        self._infection_chance = 0.25
        self._flee_chance_low_hp = 0.10
        self._flee_threshold = 0.15
        self._infection_damage_base = 5.0
        self._infection_turns = 3

    def before_turn(self, player: 'Player'):
        if random() < self._infection_chance:
            player.apply_status("infection", self._infection_damage_base, self._infection_turns)
        if self._hp / self._max_hp < self._flee_threshold and random() < self._flee_chance_low_hp:
            print("Крыса сбежала!")
            player.end_fight()

    def to_dict(self):
        return {
            "class": "Rat",
            "lvl": self._lvl,
            "reward_coins": self._reward_coins, 
            "position": self._position
        }
    
    @classmethod
    def from_dict(cls, data):
        instance = cls(lvl=data["lvl"], position=tuple(data["position"]))
        return instance

CLASS_REGISTRY["Rat"] = Rat

class Spider(Enemy):

    def __init__(self, lvl: int, position: tuple[int, int]):
        hp = 100*(1+lvl/10)
        max_dmg = 20*(1+lvl/10)
        super().__init__(lvl, hp, max_dmg, 250, position)
        self._poison_chance = 0.10
        self._poison_damage_base = 15.0
        self._poison_turns = 2
        self._summon_chance_low_hp =0.10
        self._call_threshold = 0.15

    def before_turn(self, player: 'Player'):
        if random() < self._poison_chance:
            player.apply_status("poison", self._poison_damage_base, self._poison_turns)
        if self._hp / self._max_hp < self._call_threshold and random() < self._summon_chance_low_hp:
            print("Паук призвал подкрепление!")

    def to_dict(self):
        return {
            "class": "Spider",
            "lvl": self._lvl,
            "reward_coins": self._reward_coins, 
            "position": self._position 
        }

    @classmethod
    def from_dict(cls, data):
        instance = cls(lvl=data["lvl"],  position=tuple(data["position"]))
        return instance

CLASS_REGISTRY["Spider"] = Spider


class Skeleton(Enemy):

    def __init__(self, lvl: int, position: tuple[int, int]):
        hp = 100 * (1 + lvl / 10)
        max_dmg = 10 * (1 + lvl / 10)
        super().__init__(lvl, hp, max_dmg, 150, position)
        self._weapon = choice([Fist(position), Stick(position), Bow(position), Revolver(position)])

    def attack(self, target):
        dmg = self._weapon.roll_damage()
        target.take_damage(dmg)
        return dmg

    def before_turn(self, player:'Player'):
        pass

    def drop_loot(self):
        return self._weapon if not isinstance(self._weapon, Fist) else None
    
    def to_dict(self):
        weapon_data = self._weapon.to_dict() if self._weapon else None

        return {
            "class": "Skeleton",
            "lvl": self._lvl,
            "reward_coins": self._reward_coins, 
            "position": self._position, 
            "weapon": weapon_data
        }

    @classmethod
    def from_dict(cls, data):
        instance = cls(lvl = data["lvl"], position=tuple(data["position"]))
        if data["weapon"]:
            instance._weapon = load_object(data["weapon"])
        return instance

CLASS_REGISTRY["Skeleton"] = Skeleton

@register_class
class Player(Entity, Damageable, Attacker):
    def __init__(self, lvl: int, position: tuple[int, int]):
        Entity.__init__(self, position)
        max_hp = 150 * (1 + lvl / 10)
        Damageable.__init__(self, hp=max_hp, max_hp=max_hp)
        self._lvl = lvl
        self._weapon = Fist(position)
        self._inventory = {
            "Medkit": [], "Rage": [], "Arrows": [], "Bullets": [], "Accuracy": []
        }
        self._coins = 0

        self._rage = 1.0
        self._accuracy = 1.0
        self._statuses = {}
        self._fight = False

    def symbol(self):
        return "P"

    def move(self, d_row: int, d_col: int, board: 'Board'):
        new_pos = (self._position[0] + d_row, self._position[1]+d_col)
        if not board.in_bounds(new_pos):
            print("Нельзя выйти за пределы поля!")
            return False
        self._position = new_pos


    def attack(self, target: Damageable):
        if isinstance(self._weapon, MeleeWeapon):
            dmg = self._weapon.damage(self._rage)
        elif isinstance(self._weapon, RangedWeapon):
            dmg = self._weapon.damage(self._accuracy)
        else:
            dmg = randint(0, 20)
        target.take_damage(dmg)
        return dmg

    def choose_weapon(self, new_weapon: Weapon):
        print(f"Найдено оружие: {new_weapon._name}. Заменить? (y/n)")
        if input().strip().lower() == 'y':
            self._weapon = new_weapon
            print(f"Оружие заменено на {new_weapon._name}")

    def apply_status_tick(self):
        total_damage = 0.0
        for status, (dmg, turns) in list(self._statuses.items()):
            real_dmg = dmg * (1 + self._lvl / 10)
            taken = self.take_damage(real_dmg)
            total_damage += taken
            if turns <= 1:
                del self._statuses[status]
                print(f"Статус {status} закончился")
            else:
                self._statuses[status] = (dmg, turns - 1)
        return total_damage

    def apply_status(self, name: str, dmg: float, turns):
        self._statuses[name] = (dmg, turns)

    def add_coins(self, amount: int):
        self._coins += amount

    def add_to_inventory(self, name, bonus):
        self._inventory[name].append(bonus)
        print(f"Бонус {name} добавлен в инвентарь")

    def use_bonus(self):
        available = [k for k, v in self._inventory.items() if v]
        if not available:
            print("Инвентарь пуст.")
            return
        print("Выберите бонус:", ", ".join(available))
        choice_name = input().strip()
        if choice_name in available:
            bonus = self._inventory[choice_name].pop()
            bonus.apply(self)
        else:
            print("Неверный выбор.")

    def buy_auto_if_needed(self, bonus_type: str):
        prices = {"Medkit": 75, "Rage": 50, "Accuracy": 50}
        if bonus_type not in prices:
            return None
        if self._coins < prices[bonus_type]:
            print("Недостаточно монет!")
            return None
        self._coins -= prices[bonus_type]
        cls = globals()[bonus_type]
        bonus = cls(self._position)
        bonus.apply(self)
        return bonus

    @property
    def fight(self):
        return self._fight

    def change_fight(self):
        self._fight = not self._fight

    def end_fight(self):
        self._fight = False

    def has_status(self):
        return len(self._statuses) > 0
    
    def to_dict(self):
        weapon_data = self._weapon.to_dict() if self._weapon else None
        return {
            "class": "Player",
            "position": self.position,
            "hp": round(self._hp, 1),
            "max_hp": self._max_hp,
            "lvl": self._lvl,
            "weapon": weapon_data,
            "coins": self._coins,
            "rage": round(self._rage, 2),
            "accuracy": round(self._accuracy, 2),
            "statuses": dict(self._statuses),
            "inventory": {name: len(items) for name, items in self._inventory.items()},
            "fight": self._fight
        }

    @classmethod
    def from_dict(cls, data):
        position = tuple(data["position"])
        lvl = data["lvl"]
        player = cls(lvl=lvl, position=position)
        player._hp = data["hp"]
        player._max_hp = data["max_hp"]
        player._coins = data["coins"]
        player._rage = data["rage"]
        player._accuracy = data["accuracy"]
        player._fight = data["fight"]
        player._statuses = dict(data["statuses"]) if data["statuses"] else {}
        player._inventory = {name: [] for name in ["Medkit", "Rage", "Arrows", "Bullets", "Accuracy"]}
        
        if data["weapon"]:
            player._weapon = load_object(data["weapon"])
        else:
            player._weapon = Fist(position)
        
        return player
    
CLASS_REGISTRY["Player"] = Player

class Board:
    def __init__(self, rows: int, cols: int):
        self._rows = rows
        self._cols = cols
        self._grid = [
            [(None, False) for i in range(cols)] for j in range(rows)
        ]
        self._start = (0, 0)
        self._goal = (rows - 1, cols - 1)

    def in_bounds(self, pos: tuple[int, int]):
        r, c = pos
        return 0 <= r < self._rows and 0 <= c < self._cols

    def place(self, entity: Entity, pos: tuple[int, int]):
        if self.in_bounds(pos):
            self._grid[pos[0]][pos[1]] = (entity, True)

    def entity_at(self, pos: tuple[int, int]):
        if self.in_bounds(pos):
            return self._grid[pos[0]][pos[1]][0]
        return None

    def is_revealed(self, pos: tuple[int, int]):
        if self.in_bounds(pos):
            return self._grid[pos[0]][pos[1]][1]
        return False

    def reveal(self, pos: tuple[int, int]):
        if self.in_bounds(pos):
            self._grid[pos[0]][pos[1]] = (self._grid[pos[0]][pos[1]][0], True)

    def render(self, player: 'Player'):
        lines = []
        for r in range(self._rows):
            row = []
            for c in range(self._cols):
                cell_entity, revealed = self._grid[r][c]
                pos = (r, c)

                if not revealed:
                    row.append("X")
                    continue

                if pos == player.position:
                    row.append("P")
                elif cell_entity is None:
                    row.append(" ")
                else:
                    row.append(cell_entity.symbol())  
            line = "|" + "|".join(row) + "|"
            lines.append(line)
        print("\n".join(lines))

        

    def to_dict(self):
        grid_data = []
        for r in range(self._rows):
            row = []
            for c in range(self._cols):
                entity, revealed = self._grid[r][c]
                cell = {"revealed": revealed}
                if entity is None:
                    cell["entity"] = None
                else:
                    cell["entity"] = entity.to_dict()
                row.append(cell)
            grid_data.append(row)

        return {
            "class": "Board",
            "rows": self._rows,
            "cols": self._cols,
            "start": self._start,
            "goal": self._goal,
            "grid": grid_data
        }
    
    @classmethod
    def from_dict(cls, data):
        rows = data["rows"]
        cols = data["cols"]
        board = cls(rows, cols)
        board._start = tuple(data["start"])
        board._goal = tuple(data["goal"])

        grid_data = data["grid"]
        for r, row in enumerate(grid_data):
            for c, cell in enumerate(row):
                revealed = cell["revealed"]
                entity_data = cell["entity"]
                entity = None
                if entity_data:
                    entity = load_object(entity_data)
                board._grid[r][c] = (entity, revealed)

        return board
    
CLASS_REGISTRY["Board"] = Board


def load_object(data):
    if not isinstance(data, dict) or "class" not in data:
        return None
    class_key = data["class"]
    cls = CLASS_REGISTRY.get(class_key)
    if not cls or not hasattr(cls, "from_dict"):
        return None
    return cls.from_dict(data)
