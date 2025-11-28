from classes import*


def start():
    print("Игра 'Сдохни или умри'")
    print("Введите размеры поля:")
    n_input = input("Количество строк: ").strip()
    if n_input.isdigit() and int(n_input) > 0:
        n = int(n_input)
    else:
        print("Некорректное количество строк. Установлено: 5")
        n = 5

    m_input = input("Количество столбцов: ").strip()
    if m_input.isdigit() and int(m_input) > 0:
        m = int(m_input)
    else:
        print("Некорректное количество столбцов. Установлено: 5")
        m = 5

    lvl_input = input("Уровень игрока (1-10): ").strip()
    if lvl_input.isdigit():
        lvl = int(lvl_input)
        if 1 <= lvl <= 10:
            pass  
        else:
            print("Уровень должен быть от 1 до 10. Установлен: 1")
            lvl = 1
    else:
        print("Некорректный ввод уровня. Установлен: 1")
        lvl = 1


    board = Board(n, m)
    player = Player(lvl=lvl, position=(0, 0))
    board.place(player, (0, 0))

    total_cells = n * m
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


def game(board: Board, player: Player):
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
            entity.interact(board)

        
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
