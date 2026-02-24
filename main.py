"""
Super cool game with two players and monsters
"""

import random
import arcade
import math
import time  # Add import for time module
from myPlayer import Hero
from myEnemy import Monster #thats very very mean
import arcade
from arcade.gui import *

WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
WINDOW_TITLE = "Monster Shooter"
PLAYER_INFO_FONT_SIZE = 14
TEX_RED_BUTTON_NORMAL = arcade.load_texture(":resources:gui_basic_assets/button/red_normal.png")
TEX_RED_BUTTON_HOVER = arcade.load_texture(":resources:gui_basic_assets/button/red_hover.png")
TEX_RED_BUTTON_PRESS = arcade.load_texture(":resources:gui_basic_assets/button/red_press.png")
bullet_img_list=["sprites/Pistol_bullet.png", ":resources:images/space_shooter/laserBlue01.png"]

colors = [arcade.color.RED, arcade.color.GREEN, arcade.color.BLUE, arcade.color.YELLOW, arcade.color.PURPLE]
upgrade_names = ["Health Boost", "Damage Boost", "Speed Boost", "Fire Rate Boost", "Bullet Size Boost"]
upgrade_multipliers = [100, 1.2, 1.5, 0.75, 1.1]  # Multipliers for each upgrade type
upgrade_costs = [100, 150, 120, 200, 180]  # Costs for each upgrade type

UPGRADE_SUCCESS_SOUND = arcade.sound.load_sound(":resources:sounds/coin1.wav")
UPGRADE_FAIL_SOUND = arcade.sound.load_sound(":resources:sounds/error4.wav")
BUTTON_TEXTURE_NORMAL = arcade.load_texture(":resources:gui_basic_assets/button/red_normal.png")
BUTTON_TEXTURE_HOVER = arcade.load_texture(":resources:gui_basic_assets/button/red_hover.png")
BUTTON_TEXTURE_PRESS = arcade.load_texture(":resources:gui_basic_assets/button/red_press.png")

WIN_CONDITION = 10  # Number of waves to win the game

class TitleView(arcade.View):
    """ Title screen view. """

    def __init__(self):
        super().__init__()
        self.ui = UIManager()
        self.background_color = arcade.color.BLIZZARD_BLUE

    def on_show_view(self):
        self.ui.enable()
        self.setup_ui()

    def on_hide_view(self):
        self.ui.disable()

    def setup_ui(self):
        """ Set up the title screen UI. """
        self.ui.disable()
        self.ui = UIManager()
        self.ui.enable()

        anchor = self.ui.add(UIAnchorLayout())

        # Add a start button
        start_button = UITextureButton(
            text="Start Game",
            texture=BUTTON_TEXTURE_NORMAL,
            texture_hovered=BUTTON_TEXTURE_HOVER,
            texture_pressed=BUTTON_TEXTURE_PRESS,
            width=300
        )
        anchor.add(start_button, align_x=0, align_y=0)
        @start_button.event("on_click")
        def on_click(event):
            game_view = GameView()
            game_view.setup()
            arcade.schedule(game_view.on_update, 1 / 60)  # Schedule the game update loop
            self.window.show_view(game_view)

    def on_draw(self):
        """ Render the title screen. """
        self.clear()
        arcade.draw_text("Monster Shooter", WINDOW_WIDTH // 2, WINDOW_HEIGHT - 200,
                         arcade.color.BLACK, font_size=50, anchor_x="center")
        self.ui.draw()

class GameOverView(arcade.View):
    """ Game over screen view. """

    def __init__(self, wave):
        super().__init__()
        self.wave = wave
        self.ui = UIManager()
        self.background_color = arcade.color.BLIZZARD_BLUE

    def on_show_view(self):
        self.ui.enable()
        self.setup_ui()

    def on_hide_view(self):
        self.ui.disable()

    def setup_ui(self):
        """ Set up the game-over screen UI. """
        self.ui.disable()
        self.ui = UIManager()
        self.ui.enable()

        anchor = self.ui.add(UIAnchorLayout())

        # Add a return to title button
        return_button = UITextureButton(
            text="Return to Title",
            texture=BUTTON_TEXTURE_NORMAL,
            texture_hovered=BUTTON_TEXTURE_HOVER,
            texture_pressed=BUTTON_TEXTURE_PRESS,
            width=300
        )
        anchor.add(return_button, align_x=0, align_y=0)
        @return_button.event("on_click")
        def on_click(event):
            title_view = TitleView()
            self.window.show_view(title_view)

    def on_draw(self):
        """ Render the game-over screen. """
        self.clear()
        arcade.draw_text("Game Over", WINDOW_WIDTH // 2, WINDOW_HEIGHT - 200,
                         arcade.color.RED, font_size=50, anchor_x="center")
        arcade.draw_text(f"You reached wave {self.wave}", WINDOW_WIDTH // 2, WINDOW_HEIGHT - 250,
                         arcade.color.GREEN, font_size=20, anchor_x="center")
        self.ui.draw()

class ShopView(arcade.View):
    """ Shop view for buying weapons or upgrades. """

    def __init__(self, game_view):
        super().__init__()
        self.background_color = arcade.color.LIGHT_GRAY
        self.game_view = game_view  # Reference to the main game view
        self.ui = UIManager()
    

    def on_show_view(self):
        self.ui.enable()
        self.setup_ui()

    def on_hide_view(self):
        self.ui.disable()

    def setup_ui(self):
        """ Set up the shop UI with textured buttons. """
        self.ui.disable()  # Disable the UI to clear existing elements
        self.ui = UIManager()  # Reinitialize the UIManager
        self.ui.enable()

        anchor = self.ui.add(UIAnchorLayout())

        # Create upgrade buttons for Player 1
        for i in range(len(upgrade_names)):
            button = UITextureButton(
                text=f"Player 1 {upgrade_names[i]} (Cost: {upgrade_costs[i]})",
                texture=BUTTON_TEXTURE_NORMAL,
                texture_hovered=BUTTON_TEXTURE_HOVER,
                texture_pressed=BUTTON_TEXTURE_PRESS,
                width=300  # Set button width to 300
            )
            anchor.add(button, align_x=-300, align_y=200 - i * 100)
            @button.event("on_click")
            def on_click(event, option=i):
                self.apply_upgrade(self.game_view.player_list[0], option)

        # Create upgrade buttons for Player 2
        for i in range(len(upgrade_names)):
            button = UITextureButton(
                text=f"Player 2 {upgrade_names[i]} (Cost: {upgrade_costs[i]})",
                texture=BUTTON_TEXTURE_NORMAL,
                texture_hovered=BUTTON_TEXTURE_HOVER,
                texture_pressed=BUTTON_TEXTURE_PRESS,
                width=300  # Set button width to 300
            )
            anchor.add(button, align_x=300, align_y=200 - i * 100)
            @button.event("on_click")
            def on_click(event, option=i):
                self.apply_upgrade(self.game_view.player_list[1], option)

        # Add a button to return to the game
        back_button = UITextureButton(
            text="Return to Game",
            texture=BUTTON_TEXTURE_NORMAL,
            texture_hovered=BUTTON_TEXTURE_HOVER,
            texture_pressed=BUTTON_TEXTURE_PRESS,
            width=300  # Set button width to 300
        )
        anchor.add(back_button, align_x=0, align_y=-300)
        @back_button.event("on_click")
        def on_click(event):
            self.window.show_view(self.game_view)

    def apply_upgrade(self, player, upgrade_index):
        """ Apply the selected upgrade to the player. """
        if player.score >= upgrade_costs[upgrade_index]:
            player.score -= upgrade_costs[upgrade_index]
            if upgrade_index == 0:  # Health Boost
                player.health += upgrade_multipliers[upgrade_index]
            elif upgrade_index == 1:  # Damage Boost
                player.damage_factor *= upgrade_multipliers[upgrade_index]
            elif upgrade_index == 2:  # Speed Boost
                player.speed *= upgrade_multipliers[upgrade_index]
            elif upgrade_index == 3:  # Fire Rate Boost
                player.weapons.current_gun.gun_cooldown *= upgrade_multipliers[upgrade_index]
            elif upgrade_index == 4:  # Bullet Size Boost
                player.weapons.current_gun.bullet_scale *= upgrade_multipliers[upgrade_index]
            arcade.sound.play_sound(UPGRADE_SUCCESS_SOUND)
            print(f"{player.playername} upgraded {upgrade_names[upgrade_index]}!")
        else:
            arcade.sound.play_sound(UPGRADE_FAIL_SOUND)
            print(f"{player.playername} does not have enough score for {upgrade_names[upgrade_index]}!")

    def on_draw(self):
        """ Render the shop screen. """
        self.clear()
        arcade.draw_text("Shop", WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100,
                         arcade.color.BLACK, font_size=50, anchor_x="center")
        self.ui.draw()

        # Display wave counter
        arcade.draw_text(f"Wave: {self.game_view.wave}", WINDOW_WIDTH // 2, WINDOW_HEIGHT - 150,
                         arcade.color.BLACK, font_size=20, anchor_x="center")

        # Player 1 stats on the left corner
        stats_x_p1 = 50
        arcade.draw_text("Player 1 Stats:", stats_x_p1, WINDOW_HEIGHT - 200,
                         arcade.color.BLACK, font_size=20)
        arcade.draw_text(f"Coins: {self.game_view.player_list[0].score}", stats_x_p1, WINDOW_HEIGHT - 230,
                         arcade.color.BLACK, font_size=16)
        arcade.draw_text(f"Health: {self.game_view.player_list[0].health:.1f}", stats_x_p1, WINDOW_HEIGHT - 260,
                         arcade.color.BLACK, font_size=16)
        arcade.draw_text(f"Ammo: {self.game_view.player_list[0].weapons.current_gun.loaded_bullets}", stats_x_p1, WINDOW_HEIGHT - 290,
                         arcade.color.BLACK, font_size=16)
        arcade.draw_text(f"Damage: {self.game_view.player_list[0].damage_factor:.1f}", stats_x_p1, WINDOW_HEIGHT - 320,
                         arcade.color.BLACK, font_size=16)

        # Player 2 stats on the right corner
        stats_x_p2 = WINDOW_WIDTH - 300
        arcade.draw_text("Player 2 Stats:", stats_x_p2, WINDOW_HEIGHT - 200,
                         arcade.color.BLACK, font_size=20)
        arcade.draw_text(f"Coins: {self.game_view.player_list[1].score}", stats_x_p2, WINDOW_HEIGHT - 230,
                         arcade.color.BLACK, font_size=16)
        arcade.draw_text(f"Health: {self.game_view.player_list[1].health:.1f}", stats_x_p2, WINDOW_HEIGHT - 260,
                         arcade.color.BLACK, font_size=16)
        arcade.draw_text(f"Ammo: {self.game_view.player_list[1].weapons.current_gun.loaded_bullets}", stats_x_p2, WINDOW_HEIGHT - 290,
                         arcade.color.BLACK, font_size=16)
        arcade.draw_text(f"Damage: {self.game_view.player_list[1].damage_factor:.1f}", stats_x_p2, WINDOW_HEIGHT - 320,
                         arcade.color.BLACK, font_size=16)

class GameView(arcade.View):
    """ Main application class. """

    def __init__(self, num_player=2, num_type_monster=3):
        """ Initializer """
        # Call the parent class initializer
        super().__init__()
        self.num_player = num_player
        self.num_type_monster = num_type_monster
        # Variables that will hold sprite lists
        self.player_list = arcade.SpriteList()
        self.enemy_lists = []
        self.bullet_list = None
        self.min_spawns = [2, 5, 7, 9, 12, 16]  # Increased minimum spawns
        self.max_spawns = [5, 8, 10, 12, 16, 21]  # Increased maximum spawns

        # Load sounds. Sounds from kenney.nl
        self.gun_sound = arcade.sound.load_sound(":resources:sounds/laser1.wav")
        self.hit_sound = arcade.sound.load_sound(":resources:sounds/phaseJump1.wav")

        self.background_color = arcade.color.AERO_BLUE
        # # Movement attributes
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.zero_pressed = False

        self.w_pressed = False
        self.s_pressed = False
        self.a_pressed = False
        self.d_pressed = False
        self.space_pressed = False
        self.mouse_click = False

        self.q_pressed = False
        self.e_pressed = False
        self.q2_pressed = False  # Rotate Player 2 counter-clockwise
        self.e2_pressed = False  # Rotate Player 2 clockwise
        
        self.wave = 0  # Initialize the wave counter
        self.shop_opened = False  # Track if the shop is opened

        self.spawn_timer = 0  # Timer to track enemy spawn intervals
        self.spawn_delay = 10  # Delay between batches (in seconds)
        self.enemies_to_spawn = []  # Queue of enemies to spawn

        #UI
        self.ui = UIManager()

        # Create an anchor layout, which can be used to position widgets on screen
        anchor = self.ui.add(UIAnchorLayout())

    def on_hide_view(self) -> None:
        self.ui.disable()
    
    def on_draw(self):
        """ Render the screen. """
        self.clear()
        self.player_list.draw()
        for player in self.player_list:
            player.weapons.draw_weapons()  # Draw the current gun and its bullets
        for em_lst in self.enemy_lists:
            em_lst.draw()
            for emy in em_lst:
                emy.bullet_list.draw()
        self.draw_player_info()
        self.ui.draw()

    def add_enemy_list(self, m) -> arcade.SpriteList:
        """ Create a new enemy type with a random number of spirte. """
        min_spawn, max_spawn = self.min_spawns[m], self.max_spawns[m]
        n = random.randrange(min_spawn, max_spawn)
        new_enemy_list = arcade.SpriteList()
        for i in range(n):
            speed = random.uniform(0.5, m + 0.51) + 0.1 * m
            direction_bias = random.uniform(-0.5, 0.5)  # Small random factor to add variability
            if m == 0:  # Big enemy gets a speed boost
                speed += 0.5
            enemy = Monster(monster_id=m, scale=0.2, health=6 * (4 - m) ** 2, 
                            speed=speed, damage=5 - m, direction_bias=direction_bias,
                            window_width=WINDOW_WIDTH, window_height=WINDOW_HEIGHT)
            enemy.center_x = random.randrange(WINDOW_WIDTH)
            enemy.center_y = random.randrange(WINDOW_HEIGHT)
            new_enemy_list.append(enemy)
        return new_enemy_list

    def setup_players(self):
        """ Set up the player. """
        player_scales = [0.1, 0.35]
        bullet_scales = [1, 1.5]
        for i in range(self.num_player):
            # Create a player sprite
            player_sprite = Hero(image=f"sprites/Player{i+1}.png", blullet_img=bullet_img_list[i],
                                  scale=player_scales[i], skill_level=0, window_width=WINDOW_WIDTH, window_height=WINDOW_HEIGHT)
            player_sprite.center_x = 200 + i * 1000
            player_sprite.center_y = 70 + i * 800
            ## gun is now handled by the Hero's weapons class
            # gun = arcade.Sprite(f"sprites/Pistol.png", scale=0.5)
            # player_sprite.gun = gun
            self.player_list.append(player_sprite)


        
    def setup_enemies(self):
        """ Set up the enemies for the current wave. """
        self.wave += 1  # Increment the wave counter
        for player in self.player_list:
            player.damage = 5 + 5 * self.wave  # Increase player damage based on the wave
        # Increase spawn counts dynamically based on the wave
        self.min_spawns = [min_spawn + self.wave for min_spawn in self.min_spawns]
        self.max_spawns = [max_spawn + self.wave for max_spawn in self.max_spawns]

        # Prepare the enemies to spawn in batches
        self.enemies_to_spawn = []
        for i in range(self.num_type_monster):
            min_spawn, max_spawn = self.min_spawns[i], self.max_spawns[i]
            n = random.randint(min_spawn, max_spawn)
            for _ in range(n):
                self.enemies_to_spawn.append(i)  # Add enemy type to the spawn queue
        random.shuffle(self.enemies_to_spawn)  # Shuffle the spawn queue for randomness

    def spawn_enemy_batch(self):
        """ Spawn a batch of enemies from the queue. """
        batch_size = random.randint(5, 10)  # Number of enemies to spawn per batch
        for _ in range(min(batch_size, len(self.enemies_to_spawn))):
            enemy_type = self.enemies_to_spawn.pop(0)  # Get the next enemy type
            # Create a single enemy of the specified type
            speed = random.uniform(0.5, enemy_type + 0.51) + 0.1 * enemy_type
            direction_bias = random.uniform(-0.5, 0.5)  # Small random factor to add variability
            if enemy_type == 0:  # Big enemy gets a speed boost
                speed += 0.5
            enemy = Monster(monster_id=enemy_type, scale=0.2, health=6 * (4 - enemy_type) ** 2,
                            speed=speed, damage=5 - enemy_type, direction_bias=direction_bias,
                            window_width=WINDOW_WIDTH, window_height=WINDOW_HEIGHT)
            enemy.center_x = random.randrange(WINDOW_WIDTH)
            enemy.center_y = random.randrange(WINDOW_HEIGHT)
            self.enemy_lists[enemy_type].append(enemy)  # Add the enemy to the appropriate list

    def setup(self):
        """ Set up the game and reset variables. """
        self.wave = 0
        self.player_list = arcade.SpriteList()
        self.enemy_lists = [arcade.SpriteList() for _ in range(self.num_type_monster)]
        self.setup_players()
        self.setup_enemies()
        self.setup_text()
   
    def setup_text(self):
        self.p1_score = arcade.Text(
            'Player1 Score: 0', 
            10, 20,
            arcade.color.BLACK,
           PLAYER_INFO_FONT_SIZE
         )
        
        self.p2_score = arcade.Text(
            'Player1 Score: 0', 
            10, WINDOW_HEIGHT - 50,
            arcade.color.PURPLE_HEART,
           PLAYER_INFO_FONT_SIZE
         )
        
        self.p1_health = arcade.Text(
            'Player1 Health: 1000',
            10, 40,
            arcade.color.AMARANTH_PURPLE,
            PLAYER_INFO_FONT_SIZE
        )
        self.p2_health = arcade.Text(
            'Player2 Health: 1000',
            10, WINDOW_HEIGHT - 70,
            arcade.color.RED,
            PLAYER_INFO_FONT_SIZE
        )
        self.p1_ammo = arcade.Text(
            'Player1 Ammo: 0',
            10, 60,
            arcade.color.GREEN,
            PLAYER_INFO_FONT_SIZE
        )
        self.p2_ammo = arcade.Text(
            'Player2 Ammo: 0',
            10, WINDOW_HEIGHT - 90,
            arcade.color.RED,
            PLAYER_INFO_FONT_SIZE
        )
        self.p1_level = arcade.Text(
            'Player1 Ammo: 0',
            10, 80,
            arcade.color.GREEN,
            PLAYER_INFO_FONT_SIZE
        )
        self.p2_level = arcade.Text(
            'Player2 Ammo: 0',
            10, WINDOW_HEIGHT - 110,
            arcade.color.RED,
            PLAYER_INFO_FONT_SIZE
        )
        
    def draw_player_info(self):
        """ Draw player information on the screen. """
        score_textp1 = f"Player1 Coins: {self.player_list[0].score}"
        health_textp1 = f"Player1 Health: {self.player_list[0].health:.1f}"
        ammo_textp1 = f"Player1 Ammo: {self.player_list[0].weapons.current_gun.loaded_bullets}"
        level_textp1 = f"Player1 Damage: {self.player_list[0].damage_factor:.1f}"

        score_textp2 = f"Player2 Coins: {self.player_list[1].score}"
        health_textp2 = f"Player2 Health: {self.player_list[1].health:.1f}"
        ammo_textp2 = f"Player2 Ammo: {self.player_list[1].weapons.current_gun.loaded_bullets}"
        level_textp2 = f"Player2 Damage: {self.player_list[1].damage_factor:.1f}"

        self.p1_score.text = score_textp1
        self.p1_score.draw()
        self.p1_health.text = health_textp1
        self.p1_health.draw()
        self.p1_ammo.text = ammo_textp1
        self.p1_ammo.draw()
        self.p1_level.text = level_textp1
        self.p1_level.draw()

        self.p2_score.text = score_textp2
        self.p2_score.draw()
        self.p2_health.text = health_textp2
        self.p2_health.draw()
        self.p2_ammo.text = ammo_textp2
        self.p2_ammo.draw()
        self.p2_level.text = level_textp2
        self.p2_level.draw()

        # Display respawn timers for players
        current_time = time.time()
        for i, player in enumerate(self.player_list):
            if player.dead and player.respawning:
                respawn_time_left = max(0, int(player.respawn_time - current_time))
                respawn_text = f"Player {i + 1} Respawns In: {respawn_time_left}s"
                if i == 0:  # Player 1 (bottom right)
                    arcade.draw_text(respawn_text, WINDOW_WIDTH - 300, 30, arcade.color.RED, font_size=14)
                elif i == 1:  # Player 2 (top right)
                    arcade.draw_text(respawn_text, WINDOW_WIDTH - 300, WINDOW_HEIGHT - 30, arcade.color.RED, font_size=14)

        # arcade.draw_text(score_textp1, 10, 20, arcade.color.RED, 14)

        # arcade.draw_text(ammo_textp2, 10, WINDOW_HEIGHT - 90, arcade.color.PURPLE, 14)
        # arcade.draw_text(score_textp2, 10, WINDOW_HEIGHT - 50, arcade.color.PURPLE, 14)
        # arcade.draw_text(score_textp2, 10, WINDOW_HEIGHT - 50, arcade.color.PURPLE, 14)

        # Display wave counter
        wave_text = f"Wave: {self.wave}"
        arcade.draw_text(wave_text, WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30,
                         arcade.color.BLACK, font_size=20, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.NUM_8 and not self.up_pressed:  # NUM 8 for up
            self.up_pressed = True
        elif key == arcade.key.NUM_5 and not self.down_pressed:  # NUM 5 for down
            self.down_pressed = True
        elif key == arcade.key.NUM_4 and not self.left_pressed:  # NUM 4 for left
            self.left_pressed = True
        elif key == arcade.key.NUM_6 and not self.right_pressed:  # NUM 6 for right
            self.right_pressed = True
        elif key == arcade.key.W and not self.w_pressed:
            self.w_pressed = True
        elif key == arcade.key.S and not self.s_pressed:
            self.s_pressed = True
        elif key == arcade.key.A and not self.a_pressed:
            self.a_pressed = True
        elif key == arcade.key.D and not self.d_pressed:
            self.d_pressed = True
        elif key == arcade.key.SPACE and not self.space_pressed:
            self.space_pressed = True
        elif key == arcade.key.NUM_0 and not self.zero_pressed:
            self.zero_pressed = True
        elif key == arcade.key.Q and not self.q_pressed:
            self.q_pressed = True
        elif key == arcade.key.E and not self.e_pressed:
            self.e_pressed = True
        elif key == arcade.key.NUM_7 and not self.q2_pressed:  # Player 2 counter-clockwise
            self.q2_pressed = True
        elif key == arcade.key.NUM_9 and not self.e2_pressed:  # Player 2 clockwise
            self.e2_pressed = True
        elif key == arcade.key.NUM_1:  # Player 1 switch gun
            self.player_list[0].weapons.switch_gun()
        elif key == arcade.key.R:
            self.player_list[1].weapons.switch_gun()
        elif key == arcade.key.F:
            #reload gun
            self.player_list[1].weapons.current_gun.reload_gun()
        elif key == arcade.key.NUM_ADD:
            self.player_list[0].weapons.current_gun.reload_gun()
        elif key == arcade.key.M:
            # Open or close the shop
            self.open_and_close_shop()
    def on_key_release(self, key, modifiers):
        if key == arcade.key.NUM_8 and self.up_pressed:  # NUM 8 for up
            self.up_pressed = False
        elif key == arcade.key.NUM_5 and self.down_pressed:  # NUM 5 for down
            self.down_pressed = False
        elif key == arcade.key.NUM_4 and self.left_pressed:  # NUM 4 for left
            self.left_pressed = False
        elif key == arcade.key.NUM_6 and self.right_pressed:  # NUM 6 for right
            self.right_pressed = False
        elif key == arcade.key.W and self.w_pressed:
            self.w_pressed = False
        elif key == arcade.key.S and self.s_pressed:
            self.s_pressed = False
        elif key == arcade.key.A and self.a_pressed:
            self.a_pressed = False
        elif key == arcade.key.D and self.d_pressed:
            self.d_pressed = False
        elif key == arcade.key.SPACE and self.space_pressed:
            self.space_pressed = False
        elif key == arcade.key.NUM_0 and self.zero_pressed:
            self.zero_pressed = False
        elif key == arcade.key.Q and self.q_pressed:
            self.q_pressed = False
        elif key == arcade.key.E and self.e_pressed:
            self.e_pressed = False
        elif key == arcade.key.NUM_7 and self.q2_pressed:  # Player 2 counter-clockwise
            self.q2_pressed = False
        elif key == arcade.key.NUM_9 and self.e2_pressed:  # Player 2 clockwise
            self.e2_pressed = False

    def update_player_movement(self, delta_time):
        if self.shop_opened == False:
        # Update player movement
            if self.player_list[0].dead == False:
                if self.up_pressed:
                    self.player_list[0].increase_y()
                if self.down_pressed:
                    self.player_list[0].decrease_y()
                if self.left_pressed:
                    self.player_list[0].decrease_x()
                if self.right_pressed:
                    self.player_list[0].increase_x()
                if self.zero_pressed:
                    self.player_list[0].weapons.current_gun.shoot(self.player_list[0].center_x, self.player_list[0].center_y, delta_time)
                if self.q2_pressed:
                    self.player_list[0].angle -= 5  # Rotate counter-clockwise
                if self.e2_pressed:
                    self.player_list[0].angle += 5  # Rotate clockwise
            if self.player_list[1].dead == False:
                if self.w_pressed:
                    self.player_list[1].increase_y()
                if self.s_pressed:
                    self.player_list[1].decrease_y()
                if self.a_pressed:
                    self.player_list[1].decrease_x()
                if self.d_pressed:
                    self.player_list[1].increase_x()
                if self.space_pressed:
                    self.player_list[1].weapons.current_gun.shoot(self.player_list[1].center_x, self.player_list[1].center_y, delta_time)
                if self.q_pressed:
                    self.player_list[1].angle -= 5  # Rotate counter-clockwise
                if self.e_pressed:
                    self.player_list[1].angle += 5  # Rotate clockwise



    def on_update(self, delta_time):
        """ Movement and game logic """

        if self.shop_opened == False:
            # Check win condition
            if self.wave >= WIN_CONDITION:
                print("You win!")
                arcade.exit()

            # Check loss condition
            if all(player.dead for player in self.player_list):
                game_over_view = GameOverView(self.wave)
                self.window.show_view(game_over_view)
            
            for em_lst in self.enemy_lists:
                for emy in em_lst:
                    emy.move_towards_closest_player(self.player_list[0], self.player_list[1])
                    emy.update_shooting(delta_time, self.player_list[0], self.player_list[1])  # Pass players
                    for bullet in emy.bullet_list:
                        for player in self.player_list:
                            if arcade.check_for_collision(bullet, player):
                                player.take_damage(emy.damage-2)
                                bullet.remove_from_sprite_lists()
                                break
                    emy.bullet_list.update()
            
            # Update spawn timer and spawn enemy batches periodically
            self.spawn_timer += delta_time
            if self.spawn_timer >= self.spawn_delay and self.enemies_to_spawn:
                self.spawn_timer = 0
                self.spawn_enemy_batch()

            self.update_player_movement(delta_time)
            # Loop through each bullet
            for player in self.player_list:
                if player.health <= 0.1:
                    # player.remove_from_sprite_lists()
                    continue
                player.update_all(delta_time)
                for bullet in player.weapons.current_gun.bullet_list:
                    # Check this bullet to see if it hit a coin
                    for emy in self.enemy_lists:

                        hit_list = arcade.check_for_collision_with_list(bullet, emy)
                        # If it did, get rid of the bullet and play the hit sound
                        if hit_list != []:
                            bullet.remove_from_sprite_lists()

                            self.hit_sound.play()

                            # For every coin we hit, add to the score and remove the coin
                            # for enemy in hit_list:
                            hit_list[0].take_damage(player.weapons.current_gun.gun_damage*player.damage_factor)
                            if hit_list[0].health <= 0:
                                # print(f"Enemy {hit_list[0]} defeated!")
                                # Remove the enemy from the sprite lists
                                # print("Enemy removed")
                                hit_list[0].remove_from_sprite_lists()
                                player.add_score(hit_list[0].reward)
                                
                            if all(len(enemy_list) == 0 for enemy_list in self.enemy_lists):
                                # print("All enemies defeated!")
                                # Optionally, you can reset the game or spawn new enemies
                                self.setup_enemies()
                            break
                    
                        # If the bullet flies off-screen, remove it.
                        if (bullet.bottom > self.width or
                            bullet.top < 0 or
                            bullet.right < 0 or
                            bullet.left > self.width
                        ):
                            bullet.remove_from_sprite_lists()
                            break
                
            for player in self.player_list:
                for emy in self.enemy_lists:
                    hit_list = arcade.check_for_collision_with_list(player, emy)
                    if len(hit_list) > 0:
                        player.take_damage(hit_list[0].damage)
                        hit_list[0].center_x += random.randrange(100,200)
                        hit_list[0].center_y += random.randrange(100,200)
                current_time = time.time()

                if player.dead == True and player.respawning == False:
                    # print(f"Player {player.playername} is dead. Respawning...")
                    player.respawn_time = time.time() + 15
                    player.respawning = True

                if current_time >= player.respawn_time and player.respawning == True:
                    player.respawn()
                    player.respawning = False
                    player.dead = False
                    # print(f"Player {player.playername} has respawned.")

    def open_and_close_shop(self):
        """ Open the shop to buy new weapons or upgrades. """
        if not self.shop_opened:
            self.shop_opened = True
            shop_view = ShopView(self)
            self.window.show_view(shop_view)
        else:
            self.shop_opened = False
            self.window.show_view(self)

def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, fullscreen=True)

    # Create and setup the TitleView
    title_view = TitleView()
    window.show_view(title_view)

    # Start the arcade game loop
    arcade.run()

if __name__ == "__main__":
    main()