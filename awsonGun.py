import math
import arcade
from arcade import Sprite


Gun_imgs = ["sprites/Pistol.png", "sprites/AR-15.png", "sprites/Ruger-Hunting_Rifle.png"]
gun_scales = [0.45, 0.65, 0.75]  # Scale for guns corresponding to gun types
gun_distances = [125, 125, 98]  # Distance from the player to the gun for each gun type
gun_damages = [10, 6, 100]  # Damage for each gun type
gun_cooldowns = [0.25, 0.1, 1.5]  # Cooldown for each gun type in seconds
Gun_sounds = [":resources:sounds/laser1.wav"]
empty_gun_sound = ":resources:sounds/error1.wav"
bullet_distances = [20, 22.5, 11]  # Distance from the gun to the bullet spawn point for each gun type
Bullet_imgs=["sprites/Pistol_bullet.png","sprites/AR-15_bullet.png","sprites/Ruger-Hunting_Rifle_bullet.png"]
bullet_scales= [0.35, 0.12, 0.175]  # Scale for bullets corresponding to gun types
bullet_speed = [10, 7.5, 20]
#":resources:images/space_shooter/laserBlue01.png"

class Gun(Sprite): 
    '''A class representing a gun that can shoot bullets.'''
    def __init__(self, gun_image, bullet_image, current_gun_index,bullet_scale=0.35,
     gun_scale=0.5, gun_damage=5, max_bullet_per_load=50, gun_cooldown=0.2):
        super().__init__(gun_image, gun_scale)
        self.gun_damage = gun_damage
        self.angle = 0
        self.bullet_list = arcade.SpriteList()
        self.bullet_img = bullet_image
        self.gun_cooldown = gun_cooldown
        self.max_bullet_per_load = max_bullet_per_load
        self.last_shoot_time = 0
        self.bullet_scale = bullet_scale
        self.current_gun_index = current_gun_index
        self.loaded_bullets = max_bullet_per_load
        self.empty_ammo_sound = arcade.sound.load_sound(empty_gun_sound)
        self.gun_sound = arcade.sound.load_sound(":resources:sounds/laser1.wav")
        self.hit_sound = arcade.sound.load_sound(":resources:sounds/phaseJump1.wav")
        self.gun_distance = gun_distances[0]  # Distance from the player to the gun
        self.empty_ammo_sound_played = False  # Track if the empty ammo sound has been played

    def reload_gun(self):
        '''Reload the gun, resetting the last shoot time.'''
        self.last_shoot_time = 0
        self.loaded_bullets = self.max_bullet_per_load

    def update_gun_config(self, gun_index):
        # make the guns size different based on the gun type
        self.scale = gun_scales[gun_index]
        self.gun_distance = gun_distances[gun_index]
        self.texture = arcade.load_texture(Gun_imgs[gun_index])
        self.gun_damage = gun_damages[gun_index]
        # Preserve the upgraded gun_cooldown value
        default_cooldown = gun_cooldowns[gun_index]
        self.gun_cooldown = min(self.gun_cooldown, default_cooldown)  # Keep the upgraded cooldown if it's faster

    def update_gun(self, player_x, player_y, player_angle):
        self.angle = player_angle  # Update the gun's angle to match the player's angle
        self.center_x = player_x-self.gun_distance*math.sin(math.radians(player_angle))/2.5
        self.center_y = player_y-self.gun_distance*math.cos(math.radians(player_angle))/2.5

    """
    def shoot(self, delta_time):
        if self.last_shoot_time<self.gun_cooldown: # shoot only if cooldown is over
            self.last_shoot_time += delta_time 
            return
        if self.loaded_bullets <= 0:
            self.empty_ammo_sound.play()
            return
        self.loaded_bullets -= 1
        bullet = arcade.Sprite(self.bullet_img, 0.5)
        bullet.scale = self.bullet_scale
        bullet.angle = self.angle  # Adjust angle to match gun orientation
        bullet_offset = 21
        if self.current_gun_index == 2:
            bullet_offset = 12
        bullet_offset_x = 0#bullet_offset * math.cos(math.radians(self.angle+90))
        bullet_offset_y = 0#bullet_offset * math.sin(math.radians(self.angle+90))
        bullet.center_x = self.center_x+bullet_offset_x#+75 * math.cos(math.radians(bullet.angle))
        bullet.center_y = self.center_y+bullet_offset_y#+75 * math.sin(math.radians(bullet.angle))
        # bullet.change_x = math.cos(math.radians(bullet.angle)) * self.bullet_speed
        # bullet.change_y = math.sin(math.radians(bullet.angle)) * self.bullet_speed
        radians = math.radians(self.angle)
        bullet.change_x = math.cos(radians) * self.bullet_speed
        bullet.change_y = math.sin(radians) * self.bullet_speed
        self.bullet_list.append(bullet)
        self.last_shoot_time = 0
        self.gun_sound.play()
    """

    def shoot(self, px, py, delta_time):
        if self.last_shoot_time < self.gun_cooldown:
            self.last_shoot_time += delta_time 
            return

        if self.loaded_bullets <= 0:
            if not self.empty_ammo_sound_played:
                self.empty_ammo_sound.play()
                self.empty_ammo_sound_played = True  # Mark the sound as played
            return

        self.empty_ammo_sound_played = False  # Reset the flag when bullets are available
        self.loaded_bullets -= 1
        bullet = arcade.Sprite(self.bullet_img, 0.5)
        bullet.scale = self.bullet_scale
        bullet.angle = self.angle  # Visually rotate sprite to match gun

        # Calculate spawn position in front of gun
        bullet_offset = bullet_distances[self.current_gun_index]
        offset_radians = math.radians(self.angle)
        bullet_offset_x = bullet_offset * math.sin(offset_radians)
        bullet_offset_y = bullet_offset * math.cos(offset_radians)

        # bullet.center_x = px + bullet_offset_x
        # bullet.center_y = py + bullet_offset_y

        bullet.center_x = self.center_x + bullet_offset_x
        bullet.center_y = self.center_y + bullet_offset_y


        # Use corrected angle for movement
        move_radians = math.radians(self.angle) # Adjust angle to point in the direction of movement
        bullet.change_x = math.sin(move_radians+math.pi/2) * bullet_speed[self.current_gun_index]
        bullet.change_y = math.cos(move_radians+math.pi/2) * bullet_speed[self.current_gun_index]

        self.bullet_list.append(bullet)
        self.last_shoot_time = 0
        self.gun_sound.play()

    def reset_empty_ammo_sound(self):
        """Reset the empty ammo sound flag."""
        self.empty_ammo_sound_played = False

class Weapons(arcade.SpriteList):
    '''A class representing a collection of weapons.'''
    def __init__(self, n_slot: int=3):
        super().__init__()
        self.n_slot = n_slot  # Number of slots for guns
        if n_slot > len(Gun_imgs):
            raise ValueError(f"n_slot must be less than or equal to {len(Gun_imgs)}")
        self.guns = [Gun(Gun_imgs[i], Bullet_imgs[i], i, bullet_scale=bullet_scales[i], gun_damage=gun_damages[i],
                         gun_cooldown=gun_cooldowns[i]) for i in range(n_slot)]
        self.current_gun_index = 0
        self.current_gun = self.guns[self.current_gun_index]
        self.current_gun_to_draw = arcade.SpriteList()
        self.current_gun_to_draw.append(self.current_gun)
        self.current_gun.position = (0, 0)  # Set initial position to (0, 0)

        # Track upgraded cooldowns for each gun
        self.upgraded_cooldowns = gun_cooldowns.copy()

    def switch_gun(self):
        if not self.current_gun.visible:  # Prevent switching if the gun is hidden
            return
        self.current_gun_index = (self.current_gun_index + 1) % self.n_slot
        self.current_gun = self.guns[self.current_gun_index]
        self.current_gun.update_gun_config(self.current_gun_index)
        self.current_gun.gun_cooldown = self.upgraded_cooldowns[self.current_gun_index]  # Use upgraded cooldown
        self.current_gun_to_draw = arcade.SpriteList()
        self.current_gun_to_draw.append(self.current_gun)

    def apply_fire_rate_upgrade(self, multiplier: float):
        """Apply a fire rate upgrade to the current gun."""
        self.upgraded_cooldowns[self.current_gun_index] *= multiplier
        self.current_gun.gun_cooldown = self.upgraded_cooldowns[self.current_gun_index]  # Update current gun's cooldown

    def draw_weapons(self):
        self.current_gun_to_draw.draw()
        self.current_gun.bullet_list.draw()
