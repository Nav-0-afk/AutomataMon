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

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.asset_dir = os.path.join(base_dir, '..', 'assets')
        self.bg_dir = os.path.join(self.asset_dir, 'ui', 'backgrounds')

        # --- Load Fonts ---
        font_path = os.path.join(self.asset_dir, 'fonts', 'power clear bold.ttf')
        self.font = pygame.font.Font(font_path, 22)

        self.phase = "SELECT"
        self.roster = list(POKEDATA.keys())
        self.select_index = 0
        self.menu_index = 0

        self.player = None
        self.enemy = None
        self.log_lines = ["Choose your action!"]

        # --- Load UI Assets ---
        self.arrow_img = self.load_ui_img(os.path.join("ui", "arrow.png"), (20, 20))
        self.platform_img = self.load_ui_img(os.path.join("ui", "indoor2_base1.png"), (250, 75))
        self.current_bg = None

        # --- Load Status Icons for Burn/Sleep ---
        self.status_icons = {}
        try:
            status_sheet = pygame.image.load(os.path.join(self.asset_dir, "ui/statuses.png")).convert_alpha()
            w = status_sheet.get_width()
            h = status_sheet.get_height() // 7
            self.status_icons["SLP"] = status_sheet.subsurface((0, 0 * h, w, h))
            self.status_icons["BRN"] = status_sheet.subsurface((0, 2 * h, w, h))
            self.status_icons["FNT"] = status_sheet.subsurface((0, 5 * h, w, h))
        except FileNotFoundError:
            pass

            # --- Slice Animation Spritesheets ---
        self.animations = {}
        self.load_anim("fire-spin", "animations/fire blast.png", 5, 3)
        self.load_anim("scratch", "animations/scratch.png", 5, 3)
        self.load_anim("volt tackle", "animations/electric1.png", 5, 3)
        self.load_anim("Thunderbolt", "animations/Thunder2.png", 5, 3)
        self.load_anim("burn", "animations/Flames.png", 3, 1)
        self.load_anim("hydropump", "animations/water3.png", 5, 3)
        self.load_anim("grass", "animations/grass.png", 4, 3)
        self.load_anim("leech-seed", "animations/leech-seed.png", 4, 3)
        self.load_anim("solar-beam", "animations/solarbeam.png", 5, 2)
        self.load_anim("sing", "animations/sing.png", 5, 1)
        self.load_anim("fire blast", "animations/fire4.png", 5, 3)
        self.load_anim("fire", "animations/fire5.png", 5, 3)
        self.load_anim("muddy-water", "animations/muddywater.png", 5, 3)
        self.load_anim("heal", "animations/Heal5.png", 5, 3)

    def load_ui_img(self, filename, scale):
        try:
            img = pygame.image.load(os.path.join(self.asset_dir, filename)).convert_alpha()
            return pygame.transform.scale(img, scale)
        except FileNotFoundError:
            surf = pygame.Surface(scale)
            surf.fill((255, 0, 255))
            return surf

    def load_anim(self, name, filename, cols, rows):
        frames = []
        try:
            sheet = pygame.image.load(os.path.join(self.asset_dir, filename)).convert_alpha()
            w = sheet.get_width() // cols
            h = sheet.get_height() // rows

            for y in range(rows):
                for x in range(cols):
                    rect = pygame.Rect(x * w, y * h, w, h)
                    frame = sheet.subsurface(rect)
                    frame = pygame.transform.scale(frame, (w * 1.1, h * 1.1))
                    frames.append(frame)
            self.animations[name] = frames
        except FileNotFoundError:
            print(f"ANIMATION ERROR: Missing {filename}")

    # ==========================================
    # --- ANIMATION & SEQUENCING HELPERS ---
    # ==========================================

    def wait(self, ms):
        start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start < ms:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            self.clock.tick(60)

    def display_text(self, text_list):
        """Types text letter by letter at medium speed and blocks inputs"""
        self.log_lines = [""] * len(text_list)
        for i, line in enumerate(text_list):
            for char in line:
                self.log_lines[i] += char
                self.draw_battle_ui()
                pygame.display.flip()
                self.wait(25)  # Medium typewriter speed (25ms per char)
        self.wait(700)  # Pause to let player read

    def play_animation(self, anim_name, target_pkmn, target_x, target_y):
        frames = self.animations.get(anim_name, [])
        if not frames:
            self.wait(500)
            return

        sprite_w = target_pkmn.sprite.get_width()
        sprite_h = target_pkmn.sprite.get_height()
        cx = target_x + (sprite_w // 2)
        cy = target_y + (sprite_h // 2)

        for frame in frames:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            self.draw_battle_ui()

            fx = cx - (frame.get_width() // 2)
            fy = cy - (frame.get_height() // 2)
            self.screen.blit(frame, (fx, fy))

            pygame.display.flip()
            # SLOWED DOWN: 6 frames per second.
            # A 15-frame animation now takes exactly 2.5 seconds to play.
            self.clock.tick(15)

            # ==========================================

    # --- TURN LOGIC ---
    # ==========================================

    def setup_battle(self, player_name):
        self.player = Pokemon(player_name, is_player=True)
        remaining = [p for p in self.roster if p != player_name]
        self.enemy = Pokemon(random.choice(remaining), is_player=False)

        try:
            if os.path.exists(self.bg_dir):
                bg_files = [f for f in os.listdir(self.bg_dir) if f.lower().endswith('.png')]
                if bg_files:
                    chosen_bg = random.choice(bg_files)
                    img = pygame.image.load(os.path.join(self.bg_dir, chosen_bg)).convert()
                    self.current_bg = pygame.transform.scale(img, (800, 600))
        except Exception:
            self.current_bg = None

        self.phase = "BATTLE"
        self.menu_index = 0
        self.display_text([f"Wild {self.enemy.name} appeared!"])
        self.display_text(["Choose your action!"])

    def execute_turn(self):
        # ---------------------------
        # PHASE 1: PLAYER TURN
        # ---------------------------
        if self.player.state in ["q2", "q4"]:
            self.player.sleep_timer -= 1
            if self.player.sleep_timer <= 0:
                self.display_text([f"{self.player.name} woke up!"])
                self.player.state = "q1" if self.player.state == "q4" else "q0"

        can_move = self.player.state in ["q0", "q1"]
        move = self.player.moves[self.menu_index]

        if can_move:
            self.display_text([f"{self.player.name} used {move['name']}!"])

            is_heal = move['type'] == 'h'
            anim_target = self.player if is_heal else self.enemy
            tx, ty = (150, 250) if is_heal else (550, 80)
            self.play_animation(move['anim'], anim_target, tx, ty)

            if move['type'] == 'd':
                dmg = move['val']
                if self.player.state in ["q1", "q4"]: dmg = max(1, dmg // 2)
                self.enemy.apply_damage(dmg)
                self.enemy.take_action('d')
            elif move['type'] == 'h':
                self.player.apply_damage(move['val'])
                self.player.take_action('h')
            elif move['type'] == 's':
                if self.enemy.state not in ["q2", "q4"]:
                    self.enemy.take_action('s')
                    self.enemy.sleep_timer = random.randint(1, 3)
            elif move['type'] == 'b':
                # Apply initial attack damage (e.g. Fire Spin deals 25) before calculating burn
                if move.get('val', 0) > 0:
                    self.enemy.apply_damage(move['val'])
                if self.enemy.name == "Charmander":
                    self.display_text(["It had no effect! Charmander is immune."])
                else:
                    self.enemy.take_action('b')
        else:
            if self.player.state in ["q2", "q4"]:
                self.display_text([f"{self.player.name} is fast asleep."])
            else:
                self.display_text([f"{self.player.name} is incapacitated!"])

        if self.enemy.state == "q3":
            self.phase = "END"
            self.display_text(["You won! Press ENTER to restart."])
            return

        # ---------------------------
        # PHASE 2: ENEMY TURN
        # ---------------------------
        if self.enemy.state in ["q2", "q4"]:
            self.enemy.sleep_timer -= 1
            if self.enemy.sleep_timer <= 0:
                self.display_text([f"Enemy {self.enemy.name} woke up!"])
                self.enemy.state = "q1" if self.enemy.state == "q4" else "q0"

        moves_by_type = {m['type']: m for m in self.enemy.moves}
        cpu_move = None
        if self.enemy.hp < (self.enemy.max_hp * 0.3) and 'h' in moves_by_type:
            cpu_move = moves_by_type['h']
        elif self.player.state not in ["q2", "q4", "q3"] and 's' in moves_by_type:
            if random.random() < 0.6: cpu_move = moves_by_type['s']
        elif self.player.state not in ["q1", "q4", "q3"] and 'b' in moves_by_type:
            if self.player.name != "Charmander" and random.random() < 0.6: cpu_move = moves_by_type['b']

        if not cpu_move:
            dmg_moves = [m for m in self.enemy.moves if m['type'] == 'd']
            cpu_move = random.choice(dmg_moves) if dmg_moves else random.choice(self.enemy.moves)

        cpu_can_move = self.enemy.state in ["q0", "q1"]

        if cpu_can_move:
            self.display_text([f"Enemy {self.enemy.name} used {cpu_move['name']}!"])

            is_heal = cpu_move['type'] == 'h'
            anim_target = self.enemy if is_heal else self.player
            tx, ty = (550, 80) if is_heal else (150, 250)
            self.play_animation(cpu_move['anim'], anim_target, tx, ty)

            if cpu_move['type'] == 'd':
                dmg = cpu_move['val']
                if self.enemy.state in ["q1", "q4"]: dmg = max(1, dmg // 2)
                self.player.apply_damage(dmg)
                self.player.take_action('d')
            elif cpu_move['type'] == 'h':
                self.enemy.apply_damage(cpu_move['val'])
                self.enemy.take_action('h')
            elif cpu_move['type'] == 's':
                if self.player.state not in ["q2", "q4"]:
                    self.player.take_action('s')
                    self.player.sleep_timer = random.randint(1, 3)
            elif cpu_move['type'] == 'b':
                if cpu_move.get('val', 0) > 0:
                    self.player.apply_damage(cpu_move['val'])
                if self.player.name == "Charmander":
                    self.display_text(["It had no effect! Charmander is immune."])
                else:
                    self.player.take_action('b')
        else:
            if self.enemy.state in ["q2", "q4"]:
                self.display_text([f"Enemy {self.enemy.name} is fast asleep."])
            else:
                self.display_text([f"Enemy {self.enemy.name} is incapacitated!"])

        # ---------------------------
        # PHASE 3: POST-TURN TICK DAMAGE
        # ---------------------------
        if self.player.state in ["q1", "q4"]:
            self.play_animation("burn", self.player, 150, 250)
            burn_dmg = max(1, self.player.max_hp // 16)
            self.player.apply_damage(burn_dmg)
            self.display_text([f"{self.player.name} is hurt by its burn!"])

        if self.enemy.state in ["q1", "q4"]:
            self.play_animation("burn", self.enemy, 550, 80)
            burn_dmg = max(1, self.enemy.max_hp // 16)
            self.enemy.apply_damage(burn_dmg)
            self.display_text([f"Enemy {self.enemy.name} is hurt by its burn!"])

        if self.player.state == "q3":
            self.phase = "END"
            self.display_text(["You blacked out! Press ENTER to restart."])
        elif self.enemy.state == "q3":
            self.phase = "END"
            self.display_text(["You won! Press ENTER to restart."])
        else:
            self.display_text(["Choose your action!"])

    # ==========================================
    # --- DRAWING & UI ---
    # ==========================================

    def draw_text(self, text, x, y, color=(0, 0, 0), outline_color=(255, 255, 255)):
        outline = self.font.render(text, True, outline_color)
        self.screen.blit(outline, (x - 1, y))
        self.screen.blit(outline, (x + 1, y))
        self.screen.blit(outline, (x, y - 1))
        self.screen.blit(outline, (x, y + 1))

        surface = self.font.render(text, True, color)
        self.screen.blit(surface, (x, y))

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

        pygame.draw.rect(self.screen, (0, 0, 0), (x - 2, y - 2, bar_width + 4, bar_height + 4))
        pygame.draw.rect(self.screen, (100, 100, 100), (x, y, bar_width, bar_height))
        pygame.draw.rect(self.screen, bar_color, (x, y, fill_width, bar_height))

        self.draw_text(f"{hp}/{max_hp}", x + bar_width + 10, y - 5)

    def draw_status_icons(self, state, x, y):
        # Maps DFA States directly to the cropped icons loaded in __init__
        if not hasattr(self, 'status_icons') or not self.status_icons:
            return

        if state == "q1" and "BRN" in self.status_icons:
            self.screen.blit(self.status_icons["BRN"], (x, y))
        elif state == "q2" and "SLP" in self.status_icons:
            self.screen.blit(self.status_icons["SLP"], (x, y))
        elif state == "q3" and "FNT" in self.status_icons:
            self.screen.blit(self.status_icons["FNT"], (x, y))
        elif state == "q4":
            if "BRN" in self.status_icons: self.screen.blit(self.status_icons["BRN"], (x, y))
            if "SLP" in self.status_icons: self.screen.blit(self.status_icons["SLP"], (x + 35, y))

    def draw_pokemon(self, pkmn, x, y):
        self.screen.blit(self.platform_img, (x - 60, y + 85))
        self.screen.blit(pkmn.sprite, (x, y))

        self.draw_text(f"{pkmn.name}", x, y - 55)
        self.draw_health_bar(x, y - 25, pkmn.hp, pkmn.max_hp)
        self.draw_status_icons(pkmn.state, x + 120, y - 55)

        color = (0, 0, 0)
        if pkmn.state == "q0":
            color = (34, 139, 34)
        elif pkmn.state in ["q2", "q3"]:
            color = (255, 0, 0)
        elif "q" in pkmn.state:
            color = (255, 140, 0)

        self.draw_text(f"DFA: {pkmn.state}", x + 155, y, color)

    def draw_battle_ui(self):
        if self.current_bg:
            self.screen.blit(self.current_bg, (0, 0))
        else:
            self.screen.fill((240, 240, 240))

        self.draw_pokemon(self.player, 150, 250)
        self.draw_pokemon(self.enemy, 550, 80)

        pygame.draw.rect(self.screen, (255, 255, 255), (0, 450, 800, 150))
        pygame.draw.rect(self.screen, (0, 0, 0), (0, 450, 800, 150), 3)
        pygame.draw.line(self.screen, (0, 0, 0), (400, 450), (400, 600), 3)

        for i, line in enumerate(self.log_lines):
            self.draw_text(line, 20, 470 + (i * 35))

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