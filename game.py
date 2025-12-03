from classes import *
from save import *
import random

def create_level(difficulty: str, player_lvl: int = 1):
    
    settings = load("difficulty.json")
    s = settings[difficulty]

    n = random.randint(s["board_min"], s["board_max"])
    m = random.randint(s["board_min"], s["board_max"])

    board = Board(n, m)
    player = Player(lvl= player_lvl, position=(0, 0))
    board.place(player, (0, 0))

    total_cells = n*m
    goal = (n-1, m-1)
    exclude_positions = [(0, 0), goal]

    def get_random_position():
        for i in range(100):
            r = random.randint(0, n-1)
            c = random.randint(0, m - 1)
            pos = (r, c)
            if pos not in exclude_positions and board.entity_at(pos) is None:
                return pos
        return None  

    tower_count = max(1, int(total_cells*s["tower_multiplier"]))
    for i in range(tower_count):
        pos = get_random_position()
        if pos:
            board.place(Tower(pos), pos)

    weapons = [Stick, Bow, Revolver]
    weapon_count = int(total_cells * s["weapon_multiplier"])
    for i in range(weapon_count):
        pos = get_random_position()
        if pos:
            weapon_class = random.choice(weapons)
            board.place(weapon_class(pos),pos)

    bonuses = [Medkit, Rage, Arrows, Bullets, Accuracy, Coins]
    bonus_count = int(total_cells * s["bonus_multiplier"])
    for i in range(bonus_count):
        pos = get_random_position()
        if pos :
            bonus_class = random.choice(bonuses)
            board.place(bonus_class(pos), pos)

    enemies = [Rat, Spider, Skeleton]
    enemy_count=int(total_cells * s["enemy_multiplier"])
    for i in range(enemy_count):
        pos = get_random_position()
        if pos:
            enemy_class = random.choice(enemies)
            enemy_level =random.randint(1, player_lvl + 2)
            enemy = enemy_class(lvl=enemy_level, position=pos)
            board.place(enemy, pos)

    print(f"Уровень {player_lvl}: поле{n}x{m}, сложность '{difficulty}'")
    return board, player


def start():
    print("Игра Сдохни или умри")

    save_data, has_save = load_game()
    if has_save:
        current_level = save_data["current_level"]
        difficulty = save_data["difficulty"]
        print(f"Найдено сохранение. Текущий уровень: {current_level}")
        action = input("Введите 'start' для продолжения или 'new' для новой игры: ").strip().lower()
        if action == "start":
            player = Player.from_dict(save_data["player"])
            if save_data["board"] is not None:
                board = Board.from_dict(save_data["board"])
            else:
                board, player = create_level(difficulty, player_lvl=player._lvl)
                current_level+=1
            return board, player, current_level, difficulty

    print("Новая игра")
    difficulty = ""
    while difficulty not in ["easy", "normal", "hard"]:
        difficulty =input("Выберите сложность (easy/normal/hard): ").strip().lower()

    board, player = create_level(difficulty, player_lvl=1)
    return board, player, 1, difficulty


RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def game(board: Board, player: Player, current_level: int, difficulty: str):
    while True:
        board.render(player)
        if not player.is_alive():
            print(f"{RED}Вы умерли. Игра окончена.{RESET}")
            old_level, old_coins = load_record()
            if current_level > old_level or (current_level == old_level and player._coins > old_coins):
                save_record(current_level, player._coins)
                print(f"Новый рекорд: уровень {current_level}, монеты: {player._coins}")
            return

        row, col = player.position
        goal = (board._rows - 1, board._cols - 1)

        if (row, col) == goal:
            print("Поздравляем! Вы достигли цели и выжили!")
            save_game(player, None, current_level, difficulty)
            current_level += 1
            board, player = create_level(difficulty, player_lvl=player._lvl)
            continue

        if player.has_status():
            damage = player.apply_status_tick()
            if damage > 0:
                print(f"Вы получили {damage:.1f} урона от статусов.")

        entity = board.entity_at(player.position)
        if isinstance(entity, Enemy) and not player.fight:
            start_battle(player, entity, board)
            continue

        if isinstance(entity, Weapon) and entity!=player._weapon:
            print(f"{GREEN}Вы нашли оружие: {entity._name}! Сменить? (y/n){RESET}")
            player.choose_weapon(entity)
            board.place(None, player.position)

        elif isinstance(entity, Bonus):
            print(f"Вы нашли бонус: {entity.__class__.__name__}.")
            entity.apply(player)
            board.place(None, player.position)

        elif isinstance(entity, Tower):
            print(f"{YELLOW}Вы вошли в башню.{RESET}")
            entity.interact(board)

        print(f"Позиция: {player.position}, Здоровье: {player._hp:.1f}, Монеты: {player._coins}")
        print("Команды: w (вверх), s (вниз), a (влево), d (вправо), i (инвентарь), q (выход)")

        command = input("Ваш ход: ").strip().lower()

        if command == 'q' or command == 'exit':
            if player.fight:
                print("Нельзя выйти во время боя!")
            else:
                save_game(player, board, current_level, difficulty)
                print("Игра сохранена.")
                return
        elif command == 'i':
            show_inventory(player)
        elif command in ['w', 's', 'a', 'd']:
            direction_map = {'w': (-1, 0), 's': (1, 0), 'a': (0, -1), 'd': (0, 1)}
            d_row, d_col = direction_map[command]
            player.move(d_row, d_col, board)
        else:
            print("Неверная команда.")


def start_battle(player: Player, enemy: Enemy, board: Board):
    print(f"{RED}Бой начался! {enemy.__class__.__name__} (урон: {enemy._max_enemy_damage:.1f}, HP: {enemy._hp:.1f}){RESET}")
    player.change_fight()

    while player.is_alive() and enemy.is_alive():
        print(f"\nВаш ход. Здоровье: {player._hp:.1f}, Враг: {enemy._hp:.1f}")

        if player.has_status():
            damage = player.apply_status_tick()
            if damage > 0:
                print(f"Вы получили {damage:.1f} урона от статусов.")

        if any(player._inventory[key] for key in player._inventory):
            choice_input = input("Использовать бонус? (y/n): ").strip().lower()
            if choice_input == 'y':
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
    has_items = False
    for name, items in player._inventory.items():
        if items:
            print(f"{name}: {len(items)} шт.")
            has_items = True
    if not has_items:
        print("Инвентарь пуст.")
    print(f"Монеты: {player._coins}")
    cmd = input("Команды: 'use' — применить, любой другой — назад: ").strip().lower()
    if cmd == 'use':
        player.use_bonus()

if __name__ == "__main__":
    board, player, level, diff = start()
    game(board, player, level, diff)