import pygame
import os
from engine import process_turn

# Data of all the pokemons present in the game
POKEDATA = {
    "Bulbasaur": {
        "hp": 100, "sprite": "bulbasaur.gif", "back_sprite": "bulbasaur_b.gif",
        "moves": [
            {"name": "Razor Leaf", "type": "d", "val": 25, "anim": "grass"},
            {"name": "Solar Beam", "type": "d", "val": 45, "anim": "solar-beam"},
            {"name": "Sleep Powder", "type": "s", "val": 0, "anim": "sing"},
            {"name": "Synthesis", "type": "h", "val": -30, "anim": "heal"}
        ]
    },
    "Charmander": {
        "hp": 100, "sprite": "charmander.gif", "back_sprite": "charmander_b.gif",
        "moves": [
            {"name": "Flamethrower", "type": "d", "val": 25, "anim": "fire"},
            {"name": "Fire Blast", "type": "d", "val": 45, "anim": "fire blast"},
            {"name": "Fire Spin", "type": "b", "val": 25, "anim": "fire-spin"},
            {"name": "Rest", "type": "r", "val": -50, "anim": "heal"}
        ]
    },
    "Squirtle": {
        "hp": 100, "sprite": "squirtle.gif", "back_sprite": "squirtle_b.gif",
        "moves": [
            {"name": "Scratch", "type": "d", "val": 30, "anim": "scratch"},
            {"name": "Hydro Pump", "type": "d", "val": 45, "anim": "hydropump"},
            {"name": "Muddy Water", "type": "x", "val": 20, "anim": "muddy-water"},
            {"name": "Aqua Ring", "type": "h", "val": -25, "anim": "heal"}
        ]
    },
    "Pikachu": {
        "hp": 90, "sprite": "pikachu.gif", "back_sprite": "pikachu_b.gif",
        "moves": [
            {"name": "Thunderbolt", "type": "d", "val": 35, "anim": "Thunderbolt"},
            {"name": "Volt Tackle", "type": "p", "val": 40, "anim": "volt tackle"},
            {"name": "Sing", "type": "s", "val": 0, "anim": "sing"},
            {"name": "Potion", "type": "h", "val": -25, "anim": "heal"}
        ]
    }
}

class Pokemon:
    def __init__(self, name, is_player=False):
        data = POKEDATA[name]
        self.name = name
        self.max_hp = self.hp = data["hp"]
        self.moves = data["moves"]
        self.state = "q0"
        self.sleep_timer = 0

        base_dir = os.path.dirname(os.path.abspath(__file__))
        sprite_filename = data["back_sprite"] if is_player else data["sprite"]
        sprite_path = os.path.join(base_dir, '..', 'assets', 'sprites', sprite_filename)

        try:
            image = pygame.image.load(sprite_path).convert_alpha()
            self.sprite = pygame.transform.scale(image, (image.get_width() * 3, image.get_height() * 3))
        except FileNotFoundError:
            self.sprite = pygame.Surface((150, 150))
            self.sprite.fill((0, 255, 0) if is_player else (255, 0, 0))

    def take_action(self, action_input):
        new_state, can_attack = process_turn(self.state, action_input)
        self.state = new_state
        return can_attack

    def apply_damage(self, amount):
        self.hp -= amount
        if self.hp > self.max_hp: self.hp = self.max_hp
        if self.hp <= 0:
            self.hp = 0
            self.take_action('f')