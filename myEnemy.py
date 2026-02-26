from arcade import Sprite
import math
import random
import arcade
import time
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
monster_img_list = ["sprites/Enemy_big.png", "sprites/Enemy_normal.png","sprites/Enemy_small.png", ["sprites/Enemy_tiny.png", "sprites/Enemy_tiny_orange.png",
                     "sprites/Enemy_tiny_yellow.png", "sprites/Enemy_tiny_green.png", 
                          "sprites/Enemy_tiny_blue.png", "sprites/Enemy_tiny_purple.png"], "sprites/Enemy_boss.png"]
bullet_scales = [1.5, 1, 0.5, 0.25, 5]  # Scale for bullets corresponding to monster sizes
class Monster(Sprite):
    def __init__(self, monster_id, scale=1.0, health=1, speed=2.0, damage=5, direction_bias=0,
                 window_width=800, window_height=600, bullet_image=":resources:images/space_shooter/laserRed01.png",
                 parent_list=None):
        if monster_id == 3:  # Tiny monster
            image = random.choice(monster_img_list[3])  # Randomly select a tiny monster skin

        else:
            image = monster_img_list[monster_id]
        super().__init__(image, scale)
        self.monster_id = monster_id  # Unique identifier for the monster
        self.health = health
        self.speed = speed
        self.damage = damage
        self.reward = self.monster_reward()  # Calculate the reward based on monster attributes
        self.direction_bias = direction_bias  # Bias for movement direction, can be used to influence monster behavior
        self.window_width = window_width
        self.window_height = window_height
        self.bullet_list = arcade.SpriteList()
        self.bullet_image = bullet_image
        self.shoot_timer = 0  # Timer to control shooting frequency
        self.parent_list = parent_list  # Reference to the parent sprite list

    def monster_reward(self):
        return int((self.health * self.speed * self.damage)/30)

    def move(self, dx, dy):
        self.center_x += dx * self.speed
        self.center_y += dy * self.speed
        if self.center_x < 0:
            self.center_x = self.window_width-10
        elif self.center_x > self.window_width:
            self.center_x = 10
        if self.center_y < 0:
            self.center_y = self.window_height-10
        elif self.center_y > self.window_height:
            self.center_y = 10

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()  # Remove the monster from the game if health is zero or below
    
    def calculate_distance(self, sprite1, sprite2):
        dx = sprite2.center_x - sprite1.center_x
        dy = sprite2.center_y - sprite1.center_y
        return math.hypot(dx, dy)  # Returns the Euclidean distance

    def calculate_wrapped_distance(self, sprite1, sprite2):
        """ Calculate the shortest distance considering boundary wrapping. """
        dx = sprite2.center_x - sprite1.center_x
        dy = sprite2.center_y - sprite1.center_y

        # Adjust for wrapping horizontally
        if abs(dx) > self.window_width / 2:
            dx = dx - self.window_width if dx > 0 else dx + self.window_width

        # Adjust for wrapping vertically
        if abs(dy) > self.window_height / 2:
            dy = dy - self.window_height if dy > 0 else dy + self.window_height

        return dx, dy

    def move_towards_closest_player(self, player1, player2):
        # Calculate the distance to both players
        distance_to_player1 = self.calculate_distance(self, player1)
        distance_to_player2 = self.calculate_distance(self, player2)

        # Determine which player is closer
        closest_player = player1 if distance_to_player1 < distance_to_player2 else player2

        # Calculate direction to the closest player considering boundary wrapping
        dx, dy = self.calculate_wrapped_distance(self, closest_player)

        # Calculate angle to the target
        angle = math.atan2(dy, dx) + self.direction_bias  # Add a small random factor to the angle

        # Move towards the closest player
        self.move(math.cos(angle), math.sin(angle))

    def shoot(self, closest_player):
        """ Enemy shoots a bullet towards the closest player. """
        bullet_scale = bullet_scales[self.monster_id]  # Get the bullet scale based on monster size
        bullet = arcade.Sprite(self.bullet_image, bullet_scale)
        bullet.center_x = self.center_x
        bullet.center_y = self.center_y

        # Calculate direction to the closest player
        dx = closest_player.center_x - self.center_x
        dy = closest_player.center_y - self.center_y
        angle = math.atan2(dy, dx)
        bullet.angle = -math.degrees(angle) + 90 # Normalize angle to [0, 360)
        # Set bullet velocity
        bullet.change_x = math.cos(angle) * 3.5
        bullet.change_y = math.sin(angle) * 3.5

        # Rotate the bullet sprite to point in the direction of its velocity
        

        self.bullet_list.append(bullet)

    def update_shooting(self, delta_time, player1, player2):
        """ Update shooting logic. """
        if self.monster_id == 3:  # Tiny enemies cannot shoot
            return
        self.shoot_timer += delta_time
        if self.shoot_timer > random.uniform(7.5, 12.5):  # Shoot every 2 seconds
            # Determine the closest player
            distance_to_player1 = self.calculate_distance(self, player1)
            distance_to_player2 = self.calculate_distance(self, player2)
            closest_player = player1 if distance_to_player1 < distance_to_player2 else player2

            # Shoot towards the closest player
            self.shoot(closest_player)
            self.shoot_timer = 0

class Boss(Monster):
    """ Boss enemy class. """

    def __init__(self, **kwargs):

        
        super().__init__(**kwargs)
        self.scale = 0.6  # Boss is 3 times bigger than the big enemy
        self.health = 1000  # High health for the boss
        self.damage = 25  # High damage
        self.laser_cooldown = 3  # Cooldown for the massive laser
        self.last_laser_time = 0
        self.monster_id = 4

    def shoot_laser(self, delta_time, players):
        """ Shoot a massive laser at players. """
        current_time = time.time()
        if current_time - self.last_laser_time >= self.laser_cooldown:
            self.last_laser_time = current_time
            for player in players:
                if not player.dead:
                    """ Enemy shoots a bullet towards the closest player. """
                    bullet_scale = bullet_scales[self.monster_id]  # Get the bullet scale based on monster size
                    bullet = arcade.Sprite(self.bullet_image, bullet_scale)
                    bullet.center_x = self.center_x
                    bullet.center_y = self.center_y

                    # Calculate direction to the closest player
                    dx = player.center_x - self.center_x
                    dy = player.center_y - self.center_y
                    angle = math.atan2(dy, dx)
                    bullet.angle = -math.degrees(angle) + 90 # Normalize angle to [0, 360)
                    # Set bullet velocity
                    bullet.change_x = math.cos(angle) * 3.5
                    bullet.change_y = math.sin(angle) * 3.5