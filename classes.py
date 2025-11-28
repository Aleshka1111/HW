import save
from abc import ABC, abstractmethod
from random import randint, random, choice

# абстрактные классы

class Entity(ABC):

    """все сущности на доске"""

    def __init__(self, position: tuple[int, int]):
        self._position = position

    @property
    def position(self):
        return self._position

    @abstractmethod
    def symbol(self):
        pass


class Damageable(ABC):

    """те кто может принимать урон"""

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

    """те кто могут атаковать"""

    @abstractmethod
    def attack(self, target: Damageable):
        pass

# оружие
class Weapon(Entity):
    """абстракция оружия"""
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

    """аюстракция оружия ближнего боя"""

    def damage(self, rage: float):
        return self.roll_damage() * rage
    
    def to_m_dict(self):
        weapon_dict={"name": self._name, "max_damage": self._max_damage, 
                     "position":self._position}
        return weapon_dict

    @staticmethod
    def to_m_weapon(weapon_dict):
        weapon = MeleeWeapon(weapon_dict["name", "max_damage", "position"])
        return weapon

class RangedWeapon(Weapon):

    """абстракция оружия дальнего боя"""
    
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
    
    def to_r_dict(self):
        weapon_dict={"name": self._name, "max_damage": self._max_damage, 
                     "ammo": self._ammo, "position":self._position }
        return weapon_dict

    @staticmethod
    def to_r_weapon(weapon_dict):
        weapon = RangedWeapon(weapon_dict["name", "max_damage", "position", "ammo"])
        return weapon


# конкретные виды оружия

class Fist(MeleeWeapon):

    """Стартовое оружие. Максимальный урон: 20. зависит от ярости"""

    def __init__(self, position: tuple[int, int]):
        super().__init__(name="Кулак", max_damage=20, position=position)

    def roll_damage(self):
        return randint(0,int(self._max_damage))


    def damage(self, rage:float):
        return self.roll_damage()*rage


class Stick(MeleeWeapon):

    """Максимальный урон: 25. Имеет уровень прочности. После того, как прочность оказалась на нуле, то палка ломается."""

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


class Bow(RangedWeapon):

    """Максимальный урон: 35. Стрелять можно только стрелами. 
    Если стрелы закончились, то лук становится недоступен. Лук расходует на выстрел 1 стрелу."""

    def __init__(self, position):
        ammo = randint(10, 15)
        super().__init__(name = "Лук", max_damage = 35, ammo = ammo, position = position)

    def roll_damage(self):
        return randint(0, int(self._max_damage))


class Revolver(RangedWeapon):

    """Максимальный урон: 45. Стрелять можно только патронами. 
    Если патроны закончились, то револьвер становится недоступен. 
    Револьвер расходует на выстрел 2 патрона."""

    def __init__(self, position: tuple[int, int]):
        ammo = randint(5, 10)
        super().__init__(name = "Револьвер", max_damage=45, ammo=ammo, position=position)

    def roll_damage(self):
        return randint(0, int(self._max_damage))


# бонусы

class Bonus(Entity):

    """абстракция бонуса"""

    def __init__(self, position: tuple[int, int]):
        super().__init__(position)

    @abstractmethod
    def apply(self, player):
        pass

    def symbol(self):
        return "B"


class Medkit(Bonus):

    """Увеличивает здоровье, но не выше максимального. Одноразовое применение. 
    Сила аптечки определяется случайным значением от 10 до 40 в момент создания объекта. Стоимость аптечки - 75 монет."""

    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self._power = randint(10, 40)

    def apply(self, player: 'Player'):
        if player.fight:
            healed = player.heal(self._power)
            print(f"+{healed} HP от аптечки")
        else:
            player.add_to_inventory("Medkit", self)


class Rage(Bonus):

    """Увеличивает урон кулаком и палкой. Одноразовое применение. 
    Сила ярости определяется случайным значением от 0.1 до 1.0 в момент создания объекта. Стоимость ярости - 50 монет."""

    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self._multiplier = 1.0 + random()

    def apply(self, player: 'Player'):
        if player.fight:
            player._rage += self._multiplier
            print(f"Ярость увеличена на {self._multiplier:.1f}")
        else:
            player.add_to_inventory("Rage", self)


class Arrows(Bonus):

    """Увеличивает кол-во стрел. Кол-во стрел определяется случайным значением от 1 до 20 в момент создания объекта. Нельзя купить."""

    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self._amount = randint(1, 20)

    def apply(self, player: 'Player'):
        if isinstance(player._weapon, Bow):
            player._weapon._ammo += self._amount
            print(f"+{self._amount} стрел")
        else:
            player.add_to_inventory("Arrows", self)


class Bullets(Bonus):

    """Увеличивает кол-во патронов. Кол-во патронов определяется случайным значением от 1 до 10 в момент создания объекта. Нельзя купить."""
    
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self._amount = randint(1, 10)

    def apply(self, player: 'Player'):
        if isinstance(player._weapon, Revolver):
            player._weapon._ammo += self._amount
            print(f"+{self._amount} патронов")
        else:
            player.add_to_inventory("Bullets", self)


class Accuracy(Bonus):

    """Повышает точность стрельбы из лука и револьвера. 
    Сила точности определяется случайным значением от 0.1 до 1.0 в момент создания объекта. Стоимость - 50 монет."""

    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self._multiplier = 0.1 + random() * 0.9

    def apply(self, player: 'Player'):
        if player.fight:
            player._accuracy += self._multiplier
            print(f"Точность увеличена на {self._multiplier:.1f}")
        else:
            player.add_to_inventory("Accuracy", self)


class Coins(Bonus):

    """монеты"""

    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self._amount = randint(50, 100)

    def apply(self, player: 'Player'):
        player.add_coins(self._amount)
        print(f"+{self._amount} монет")


# постройки

class Structure(Entity):

    """абстракция построек"""

    def __init__(self, position: tuple[int, int]):
        super().__init__(position)

    @abstractmethod
    def interact(self, player: 'Player', board: 'Board'):
        pass

    def symbol(self):
        return "T"


class Tower(Structure):

    """Открывает на поле соседние клетки радиусом 2."""

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


# виды врагов

class Enemy(Entity, Damageable, Attacker):

    """абстракция врага"""

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

    """Во время боя с вероятностью в 25% крыса может заразить игрока на 3 хода. 
    В этом случае перед ходом игрока с него дополнительно снимается `5 * (1 + lvl / 10)`. 
    С вероятностью в 10% при низком уровне здоровья (ниже 15%) крыса может убежать.
    Если крыса сбежала, то бой заканчивается. За победу даётся 200 монет."""

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
            return


class Spider(Enemy):

    """Во время боя с вероятностью в 10% паук может отравить игрока на 2 хода. В этом случае перед ходом игрока 
    с него дополнительно снимается `15 * (1 + lvl / 10)`.
    С вероятностью в 10% при низком уровне здоровья (ниже 15%) паук может призвать другого паука. 
    При этом текущий паук не убегает с поля боя. 
    Призванный паук также может призвать нового пука. За победу над каждым пауком даётся 250 монет в конце боя."""

    def __init__(self, lvl: int, position: tuple[int, int]):
        hp = 100 * (1 + lvl / 10)
        max_dmg = 20 * (1 + lvl / 10)
        super().__init__(lvl, hp, max_dmg, 250, position)
        self._poison_chance = 0.10
        self._poison_damage_base = 15.0
        self._poison_turns = 2
        self._summon_chance_low_hp = 0.10
        self._call_threshold = 0.15

    def before_turn(self, player: 'Player'):
        if random() < self._poison_chance:
            player.apply_status("poison", self._poison_damage_base, self._poison_turns)
        if self._hp / self._max_hp < self._call_threshold and random() < self._summon_chance_low_hp:
            print("Паук призвал подкрепление!")


class Skeleton(Enemy):

    """Скелет может атаковать оружием. За победу даётся 150 монет и оружие, которое было у скелета, кроме кулака."""

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


# игрок

class Player(Entity, Damageable, Attacker):

    """игрок - персонаж, который имеет жизни, инвентарь с бонусами и оружие(только одно)"""

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
        new_pos = (self._position[0] + d_row, self._position[1] + d_col)
        if not board.in_bounds(new_pos):
            print("Нельзя выйти за пределы поля!")
            return False
        self._position = new_pos
        #return True

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
        player_dict={"position": self._position, "lvl": self._lvl, "weapon": self.weapon.to_dict(),
                     "max_hp": self._max_hp,"hp": self._hp,
                     "inventory": self._inventory, "coins": self._coins, 
                     "statuses": self._statuses, "fight": self._fight}
        return player_dict

    @staticmethod
    def to_player(player_dict):
        weapon = Weapon(**player_dict["weapon"]) 
        player = Player(player_dict["name", "lvl", weapon, "max_hp",
                                    "hp", "inventory", "coins", "statuses", "fight"])
        return player
    
# поле

class Board:
    def __init__(self, rows: int, cols: int):
        self._rows = rows
        self._cols = cols
        self._grid = [
            [(None, False) for _ in range(cols)] for _ in range(rows)
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
        grid = []
        for i in range(self._rows):
            row = []
            for j in range(self._cols):
                cell, visible = self._grid[i][j]
                if not visible:
                    row.append("X")
                elif (i, j) == player.position:
                    row.append("P")
                elif isinstance(cell, Player):
                    row.append("P")
                elif isinstance(cell, Enemy):
                    row.append("E")
                elif isinstance(cell, Tower):
                    row.append("T")
                elif isinstance(cell, Weapon):
                    row.append("W")
                elif isinstance(cell, Bonus):
                    row.append("B")
                else:
                    row.append(" ")
            grid.append("|" + "|".join(row) + "|")
            print("\n".join(grid))
        return "\n".join(grid)
    



