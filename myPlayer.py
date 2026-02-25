from arcade import Sprite
import arcade
import math
from awsonGun import Weapons
import time  # Add import for time module

damage_factor_per_level = [1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 7, 8, 9.5 , 11, 13, 15, 17, 20, 25, 30, 35, 40, 50]

class Hero(Sprite):
    def __init__(self, image, blullet_img ="sprites/Pistol_bullet.png",
     playername='Pawkel',scale=1.0, skill_level=0,
      window_width=800, window_height=600):
        super().__init__(image, scale)
        #self.health = 100*damage_factor_per_level[skill_level] if skill_level < len(damage_factor_per_level) else 100*damage_factor_per_level[-1]
        self.health = 100
        self.speed = 5
        self.score = 0
        self.skill_level = skill_level #or skill issue? jk jk
        #self.damage_factor = damage_factor_per_level[skill_level] if skill_level < len(damage_factor_per_level) else damage_factor_per_level[-1]
        self.damage_factor = 1
        self.fire_rate_multiplier = 1.0  # Track fire rate upgrades
        self.playername = playername
        self.bullet_speed = 10
        self.current_gun_index = 0
        self.bullet_scale = 0.35 if self.current_gun_index == 0 else 0.1 if self.current_gun_index == 1 else 0.1
        self.bullet_img = blullet_img
        self.bullet_list = arcade.SpriteList()
        self.window_width = window_width
        self.window_height = window_height
        self.respawn_time = 0
        self.dead = False
        self.respawning = False

        # equip player with weapon system
        self.weapons = Weapons(n_slot=3)

    def update_all(self, delta_time):
        self.update()  # Update the player's position
        self.weapons.current_gun.update_gun(self.center_x, self.center_y, self.angle)  # Update gun position
        self.weapons.current_gun.bullet_list.update()  # Update bullets

    def increase_x(self):
        self.center_x += 5
        if self.center_x > self.window_width:
            self.center_x = 10
    def increase_y(self):
        self.center_y += 5
        if self.center_y > self.window_height:
            self.center_y = 10
    def decrease_x(self):
        self.center_x -= 5
        if self.center_x < 0:
            self.center_x = self.window_width - 10
    def decrease_y(self):
        self.center_y -= 5
        if self.center_y < 0:
            self.center_y = self.window_height - 10

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0.01:
            self.center_x = -1000
            self.center_y = -1000
            self.visible = False
            self.dead = True
            self.weapons.current_gun.visible = False  # Hide the gun

    def respawn(self):
        """Respawn the player without resetting upgrades."""
        self.health = 100 * self.damage_factor  # Use upgraded health multiplier
        self.center_x = 200
        self.center_y = 200
        self.visible = True
        self.dead = False
        self.weapons.current_gun.visible = True  # Show the gun

    def add_score(self, points):
        self.score += points
        # Skill level and damage factor are now upgraded via the shop, not score.

    def on_key_release(self, key):
        """Handle key release events."""
        if key == arcade.key.SPACE:  # Player 2 shoot button
            self.weapons.current_gun.reset_empty_ammo_sound()
        elif key == arcade.key.NUM_0:  # Player 1 shoot button
            self.weapons.current_gun.reset_empty_ammo_sound()
