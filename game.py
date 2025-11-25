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
        actual = min(amount, self._max_hp - self._hp)
        self._hp += actual
        return actual

    def take_damage(self, amount: float):
        actual = min(amount, self._hp)
        self._hp -= actual
        return actual


class Attacker(ABC):
    """те кто могут атаковать"""
    @abstractmethod
    def attack(self, target: Damageable):
        pass

# оружие
class Weapon(Entity):
    """абстракция оружия"""
    def __init__(self, name: str, max_damage: float, position: tuple):
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

# конкретные виды оружия

class Fist(MeleeWeapon):
    def __init__(self, position: tuple[int, int]):
        super().__init__(name="Кулак", max_damage=20, position=position)

    def roll_damage(self):
        return randint(0, int(self._max_damage))

    def damage(self, rage:float):
        return self.roll_damage() * rage


class Stick(MeleeWeapon):
    def __init__(self, position: tuple[int, int]):
        super().__init__(name="Палка", max_damage=25, position=position)
        self._durability = randint(10, 20)

    def roll_damage(self):
        return randint(0, int(self._max_damage))

    def is_available(self):
        return self._durability > 0

    def damage(self, rage: float):
        if self._durability > 0:
            self._durability -= 1
            return self.roll_damage() * rage
        return 0.0


class Bow(RangedWeapon):
    def __init__(self, position):
        ammo = randint(10, 15)
        super().__init__(name="Лук", max_damage=35, ammo=ammo, position=position)

    def roll_damage(self):
        return randint(0, int(self._max_damage))


class Revolver(RangedWeapon):
    def __init__(self, position: tuple[int, int]):
        ammo = randint(5, 10)
        super().__init__(name="Револьвер", max_damage=45, ammo=ammo, position=position)

    def roll_damage(self):
        return randint(0, int(self._max_damage))


# бонусы

class Bonus(Entity):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)

    @abstractmethod
    def apply(self, player):
        pass

    def symbol(self):
        return "B"


class Medkit(Bonus):
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
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self._amount = randint(50, 100)

    def apply(self, player: 'Player'):
        player.add_coins(self._amount)
        print(f"+{self._amount} монет")


# постройки

class Structure(Entity):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)

    @abstractmethod
    def interact(self, player: 'Player', board: 'Board'):
        pass

    def symbol(self):
        return "T"


class Tower(Structure):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self._reveal_radius = 2

    def interact(self, player: 'Player', board: 'Board'):
        r, c = self._position
        for dr in range(-self._reveal_radius, self._reveal_radius + 1):
            for dc in range(-self._reveal_radius, self._reveal_radius + 1):
                nr, nc = r + dr, c + dc
                if board.in_bounds((nr, nc)):
                    board.reveal((nr, nc))
        print("Башня открыла окрестности!")


# виды врагов

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
            return


class Spider(Enemy):
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
        return True

    def attack(self, target: Damageable):
        print(f"Тип оружия: {type(self._weapon)}")
        print(f"Является ли объектом? {hasattr(self._weapon, 'is_available')}")
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
        return "\n".join(grid)


# игра

def start():
    print("Игра 'Сдохни или умри'")
    print("Введите размеры поля:")
    try:
        n = int(input("Количество строк: "))
        m = int(input("Количество столбцов: "))
        lvl = int(input("Уровень игрока (1-10): "))
        if not (1 <= lvl <= 10):
            print("Уровень должен быть от 1 до 10. Установлен 1.")
            lvl = 1
    except ValueError:
        print("Некорректный ввод. Установлено 5x5, уровень 1.")
        n = m = 5
        lvl = 1

    board = Board(n, m)
    player = Player(lvl=lvl, position=(0, 0))
    board.place(player, (0, 0))

    total_cells = n * m

    
    tower_count = max(1, int(total_cells * 0.01))
    for _ in range(tower_count):
        pos = (randint(0, n-1), randint(0, m-1))
        if pos != (0, 0) and pos != (n-1, m-1) and board.entity_at(pos) is None:
            tower = Tower(pos)
            board.place(tower, pos)

    
    weapons = [Stick, Bow, Revolver]
    weapon_count = int(total_cells * 0.05)
    for _ in range(weapon_count):
        pos = (randint(0, n-1), randint(0, m-1))
        if pos != (0, 0) and pos != (n-1, m-1) and board.entity_at(pos) is None:
            cls = choice(weapons)
            weapon = cls(pos)
            board.place(weapon, pos)

    
    bonuses = [Medkit, Rage, Arrows, Bullets, Accuracy, Coins]
    bonus_count = int(total_cells * 0.30)
    for _ in range(bonus_count):
        pos = (randint(0, n-1), randint(0, m-1))
        if pos != (0, 0) and pos != (n-1, m-1) and board.entity_at(pos) is None:
            cls = choice(bonuses)
            bonus = cls(pos)
            board.place(bonus, pos)

    
    enemies = [Rat, Spider, Skeleton]
    enemy_count = int(total_cells * 0.15)
    for _ in range(enemy_count):
        pos = (randint(0, n-1), randint(0, m-1))
        if pos != (0, 0) and pos != (n-1, m-1) and board.entity_at(pos) is None:
            cls = choice(enemies)
            lvl_enemy = randint(1, 10)
            enemy = cls(lvl=lvl_enemy, position=pos)
            board.place(enemy, pos)

    print(f"\nИгра инициализирована: {n}x{m}, уровень игрока {lvl}")
    print("Старт в (0,0), цель — (N-1, M-1). Удачи!\n")
    return board, player


def game(board, player):
    while True:
        if not player.is_alive():
            print("Вы умерли. Игра окончена.")
            break

        row, col = player.position
        goal = (board._rows - 1, board._cols - 1)

        if (row, col) == goal:
            print("Поздравляем! Вы достигли цели и выжили!")
            break

        
        if player.has_status():
            damage = player.apply_status_tick()
            if damage > 0:
                print(f"Вы получили {damage:.1f} урона от статусов.")

        
        entity = board.entity_at((row, col))
        if isinstance(entity, Enemy) and not player.fight:
            start_battle(player, entity, board)
            continue

        if isinstance(entity, Weapon) and entity != player._weapon:
            print(f"Вы нашли оружие: {entity._name}.")
            player.choose_weapon(entity)
            board.place(None, (row, col))

        elif isinstance(entity, Bonus):
            print(f"Вы нашли бонус: {entity.__class__.__name__}.")
            entity.apply(player)
            board.place(None, (row, col))

        elif isinstance(entity, Tower):
            print("Вы вошли в башню.")
            entity.interact(player, board)

        
        print(f"Позиция: {player.position}, Здоровье: {player._hp:.1f}, Монеты: {player._coins}")
        print("Команды: w (вверх), s (вниз), a (влево), d (вправо), i (инвентарь), q (выход)")

        cmd = input("Ваш ход: ").strip().lower()

        if cmd == 'q':
            print("Игра завершена.")
            break
        elif cmd == 'i':
            show_inventory(player)
        elif cmd in ['w', 's', 'a', 'd']:
            d_row, d_col = {'w': (-1, 0), 's': (1, 0), 'a': (0, -1), 'd': (0, 1)}[cmd]
            player.move(d_row, d_col, board)
        else:
            print("Неверная команда.")


def start_battle(player: Player, enemy: Enemy, board: Board):
    print(f"Бой начался! {enemy.__class__.__name__} (урон: {enemy._max_enemy_damage:.1f}, HP: {enemy._hp:.1f})")
    player.change_fight()

    while player.is_alive() and enemy.is_alive():
        print(f"\nВаш ход. Здоровье: {player._hp:.1f}, Враг: {enemy._hp:.1f}")

        if player.has_status():
            damage = player.apply_status_tick()
            if damage > 0:
                print(f"Вы получили {damage:.1f} урона от статусов.")

        if any(player._inventory[k] for k in player._inventory):
            use = input("Использовать бонус? (y/n): ").strip().lower()
            if use == 'y':
                player.use_bonus()
            else:
                if not player._weapon.is_available():
                    if isinstance(player._weapon, Bow):
                        player.buy_auto_if_needed("Arrows")
                    elif isinstance(player._weapon, Revolver):
                        player.buy_auto_if_needed("Bullets")
        else:
            if not player._weapon.is_available():
                if isinstance(player._weapon, Bow):
                    player.buy_auto_if_needed("Arrows")
                elif isinstance(player._weapon, Revolver):
                    player.buy_auto_if_needed("Bullets")

        damage = player.attack(enemy)
        print(f"Вы нанесли {damage:.1f} урона.")

        if not enemy.is_alive():
            print(f"Враг повержен! +{enemy._reward_coins} монет.")
            player.add_coins(enemy._reward_coins)
            if isinstance(enemy, Skeleton):
                loot = enemy.drop_loot()
                if loot:
                    print(f"Добыто: {loot._name}!")
                    player.choose_weapon(loot)
            break

        enemy.before_turn(player)
        if not enemy.is_alive():
            break

        enemy_damage = enemy.attack(player)
        print(f"Враг нанёс {enemy_damage:.1f} урона.")

        if not player.is_alive():
            print("Вы погибли.")
            break

    player.end_fight()
    if player.is_alive():
        board.place(None, player.position)


def show_inventory(player: Player):
    print("\n--- Инвентарь ---")
    for name, items in player._inventory.items():
        if items:
            print(f"{name}: {len(items)} шт.")
    print(f"Монеты: {player._coins}")
    cmd = input("Команды: 'use' — применить, любой др. — назад: ").strip().lower()
    if cmd == 'use':
        player.use_bonus()



if __name__ == "__main__":
    board, player = start()
    game(board, player)
