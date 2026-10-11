import pygame
import random
import os
from game.pokemon import Pokemon, POKEDATA


class BattleUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("AutomataMon: Finite State Battle Engine")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18, bold=True)

        self.phase = "SELECT"
        self.roster = list(POKEDATA.keys())
        self.select_index = 0
        self.menu_index = 0

        self.player = None
        self.enemy = None
        self.log_lines = ["Choose your action!"]

        # --- Load UI Assets ---
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.asset_dir = os.path.join(base_dir, '..', 'assets')
        self.bg_dir = os.path.join(self.asset_dir, 'ui', 'backgrounds')

        self.arrow_img = self.load_ui_img(os.path.join("ui", "arrow.png"), (20, 20))
        self.platform_img = self.load_ui_img(os.path.join("ui", "indoor2_base1.png"), (250, 75))

        self.current_bg = None

        # Load and slice the statuses spritesheet
        self.status_icons = {}
        try:
            status_sheet = pygame.image.load(os.path.join(self.asset_dir, "statuses.png")).convert_alpha()
            w = status_sheet.get_width()
            h = status_sheet.get_height() // 7

            self.status_icons["SLP"] = status_sheet.subsurface((0, 0 * h, w, h))
            self.status_icons["BRN"] = status_sheet.subsurface((0, 2 * h, w, h))
            self.status_icons["FNT"] = status_sheet.subsurface((0, 5 * h, w, h))
        except FileNotFoundError:
            pass

    def load_ui_img(self, filename, scale):
        try:
            img = pygame.image.load(os.path.join(self.asset_dir, filename)).convert_alpha()
            return pygame.transform.scale(img, scale)
        except FileNotFoundError:
            surf = pygame.Surface(scale)
            surf.fill((255, 0, 255))
            return surf

    def setup_battle(self, player_name):
        self.player = Pokemon(player_name, is_player=True)
        remaining = [p for p in self.roster if p != player_name]
        self.enemy = Pokemon(random.choice(remaining), is_player=False)

        # Select Random Background
        try:
            if not os.path.exists(self.bg_dir):
                print(f"BACKGROUND ERROR: Cannot find the folder exactly at {self.bg_dir}")
            else:
                bg_files = [f for f in os.listdir(self.bg_dir) if f.lower().endswith('.png')]
                if bg_files:
                    chosen_bg = random.choice(bg_files)
                    print(f"SUCCESS: Found and loading {chosen_bg}")
                    img = pygame.image.load(os.path.join(self.bg_dir, chosen_bg)).convert()
                    self.current_bg = pygame.transform.scale(img, (800, 600))
                else:
                    print(f"BACKGROUND ERROR: No .png files were found inside {self.bg_dir}")
                    self.current_bg = None
        except Exception as e:
            print(f"BACKGROUND ERROR: Pygame failed to load the image. Reason: {e}")
            self.current_bg = None

        self.phase = "BATTLE"
        self.menu_index = 0
        self.log_lines = [f"Wild {self.enemy.name} appeared!", "Choose your action!"]

    def execute_turn(self):
        self.log_lines = []

        # 1. Player Turn
        move = self.player.moves[self.menu_index]
        can_move = self.player.take_action(move['type'])

        if can_move:
            self.log_lines.append(f"{self.player.name} used {move['name']}!")
            if move['type'] == 'd':
                self.enemy.apply_damage(move['val'])
            elif move['type'] == 'h':
                self.player.apply_damage(move['val'])
            elif move['type'] in ['s', 'b']:
                self.enemy.take_action(move['type'])
        else:
            self.log_lines.append(f"{self.player.name} is incapacitated! ({self.player.state})")

        if self.enemy.state == "q3":
            self.phase = "END"
            self.log_lines.append("You won! Press ENTER to restart.")
            return

        # 2. CPU Turn (State-Aware AI)
        moves_by_type = {m['type']: m for m in self.enemy.moves}
        cpu_move = None

        if self.enemy.hp < (self.enemy.max_hp * 0.3) and 'h' in moves_by_type:
            cpu_move = moves_by_type['h']
        elif self.player.state not in ["q2", "q4", "q3"] and 's' in moves_by_type:
            if random.random() < 0.6: cpu_move = moves_by_type['s']
        elif self.player.state not in ["q1", "q4", "q3"] and 'b' in moves_by_type:
            if random.random() < 0.6: cpu_move = moves_by_type['b']

        if not cpu_move:
            cpu_move = moves_by_type.get('d', random.choice(self.enemy.moves))

        cpu_can_move = self.enemy.take_action(cpu_move['type'])

        if cpu_can_move:
            self.log_lines.append(f"Enemy {self.enemy.name} used {cpu_move['name']}!")
            if cpu_move['type'] == 'd':
                self.player.apply_damage(cpu_move['val'])
            elif cpu_move['type'] == 'h':
                self.enemy.apply_damage(cpu_move['val'])
            elif cpu_move['type'] in ['s', 'b']:
                self.player.take_action(cpu_move['type'])
        else:
            self.log_lines.append(f"Enemy {self.enemy.name} is incapacitated! ({self.enemy.state})")

        # --- Apply Post-Turn Tick Damage ---
        if self.player.state in ["q1", "q4"]:
            self.player.apply_damage(10)
            self.log_lines.append(f"{self.player.name} is hurt by its burn!")

        if self.enemy.state in ["q1", "q4"]:
            self.enemy.apply_damage(10)
            self.log_lines.append(f"Enemy {self.enemy.name} is hurt by its burn!")

        if self.player.state == "q3":
            self.phase = "END"
            self.log_lines.append("You blacked out! Press ENTER to restart.")
        elif self.enemy.state == "q3":
            self.phase = "END"
            self.log_lines.append("You won! Press ENTER to restart.")

    def draw_text(self, text, x, y, color=(0, 0, 0)):
        surface = self.font.render(text, True, color)
        self.screen.blit(surface, (x, y))

    def draw_status_icons(self, state, x, y):
        if state == "q1" and "BRN" in self.status_icons:
            self.screen.blit(self.status_icons["BRN"], (x, y))
        elif state == "q2" and "SLP" in self.status_icons:
            self.screen.blit(self.status_icons["SLP"], (x, y))
        elif state == "q3" and "FNT" in self.status_icons:
            self.screen.blit(self.status_icons["FNT"], (x, y))
        elif state == "q4":
            if "BRN" in self.status_icons: self.screen.blit(self.status_icons["BRN"], (x, y))
            if "SLP" in self.status_icons: self.screen.blit(self.status_icons["SLP"], (x + 35, y))

    def draw_health_bar(self, x, y, hp, max_hp):
        bar_width = 150
        bar_height = 12
        fill_width = (hp / max_hp) * bar_width

        ratio = hp / max_hp
        if ratio > 0.5:
            bar_color = (34, 139, 34)
        elif ratio > 0.2:
            bar_color = (255, 215, 0)
        else:
            bar_color = (255, 0, 0)

        # Restore the black border and gray background for the health bar
        pygame.draw.rect(self.screen, (0, 0, 0), (x - 2, y - 2, bar_width + 4, bar_height + 4))
        pygame.draw.rect(self.screen, (100, 100, 100), (x, y, bar_width, bar_height))
        pygame.draw.rect(self.screen, bar_color, (x, y, fill_width, bar_height))

        # HP Text beside the bar
        self.draw_text(f"{hp}/{max_hp}", x + bar_width + 10, y - 5)

    def draw_pokemon(self, pkmn, x, y):
        # 1. Base Platform and Sprite
        self.screen.blit(self.platform_img, (x - 70, y + 90))
        self.screen.blit(pkmn.sprite, (x, y))

        # 2. Text and Elements hovering directly over the sprite
        self.draw_text(f"{pkmn.name}", x, y - 55)
        self.draw_health_bar(x, y - 25, pkmn.hp, pkmn.max_hp)
        self.draw_status_icons(pkmn.state, x + 130, y - 65)

        # 3. DFA Mathematical State Tracker
        color = (0, 0, 0)
        if pkmn.state == "q0":
            color = (34, 139, 34)
        elif pkmn.state in ["q2", "q3"]:
            color = (255, 0, 0)
        elif "q" in pkmn.state:
            color = (255, 140, 0)

        self.draw_text(f"DFA: {pkmn.state}", x, y - 5, color)

    def draw_battle_ui(self):
        if self.current_bg:
            self.screen.blit(self.current_bg, (0, 0))
        else:
            self.screen.fill((240, 240, 240))

        self.draw_pokemon(self.player, 150, 250)
        self.draw_pokemon(self.enemy, 550, 80)

        # Bottom UI Box
        pygame.draw.rect(self.screen, (255, 255, 255), (0, 450, 800, 150))
        pygame.draw.rect(self.screen, (0, 0, 0), (0, 450, 800, 150), 3)
        pygame.draw.line(self.screen, (0, 0, 0), (400, 450), (400, 600), 3)

        # Log
        for i, line in enumerate(self.log_lines):
            self.draw_text(line, 20, 470 + (i * 35))

        # Grid + Image Arrow Cursor
        positions = [(440, 480), (630, 480), (440, 540), (630, 540)]
        for i, move in enumerate(self.player.moves):
            x, y = positions[i]
            if i == self.menu_index:
                self.screen.blit(self.arrow_img, (x - 25, y))
            self.draw_text(f"{move['name']}", x, y)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if self.phase == "SELECT":
                        if event.key == pygame.K_UP:
                            self.select_index = (self.select_index - 1) % 4
                        elif event.key == pygame.K_DOWN:
                            self.select_index = (self.select_index + 1) % 4
                        elif event.key == pygame.K_RETURN:
                            self.setup_battle(self.roster[self.select_index])

                    elif self.phase == "BATTLE":
                        if event.key == pygame.K_RIGHT:
                            self.menu_index = self.menu_index + 1 if self.menu_index % 2 == 0 else self.menu_index - 1
                        elif event.key == pygame.K_LEFT:
                            self.menu_index = self.menu_index - 1 if self.menu_index % 2 != 0 else self.menu_index + 1
                        elif event.key == pygame.K_DOWN:
                            self.menu_index = (self.menu_index + 2) % 4
                        elif event.key == pygame.K_UP:
                            self.menu_index = (self.menu_index - 2) % 4
                        elif event.key == pygame.K_RETURN:
                            self.execute_turn()

                    elif self.phase == "END":
                        if event.key == pygame.K_RETURN:
                            self.phase = "SELECT"

            if self.phase == "SELECT":
                self.screen.fill((200, 200, 255))
                self.draw_text("SELECT YOUR POKEMON", 250, 100)
                for i, name in enumerate(self.roster):
                    if i == self.select_index:
                        self.screen.blit(self.arrow_img, (270, 200 + (i * 40)))
                    self.draw_text(f"{name}", 300, 200 + (i * 40))

            elif self.phase == "BATTLE" or self.phase == "END":
                self.draw_battle_ui()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()