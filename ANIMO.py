import arcade
import os
from arcade.gui import UIManager
from random import randint

def ScrollSprite(theItem, theList,x, y):
    theItem.center_x = arcade.get_viewport()[0] + x
    theItem.center_y = arcade.get_viewport()[3] - y
    theList.append(theItem)

def LoadTexturePair(fileName):
    """
    Load the a in 2 conditions. Its original condition and also its flipped condition
    """
    return [arcade.load_texture(fileName), arcade.load_texture(fileName, flipped_horizontally=True)]

class KeyCollectible(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.idle_texture = 0

        self.idle_animation = []
        for i in range(8):
            texture = arcade.load_texture(f"Assets/Tiles/Key{i}.png")
            self.idle_animation.append(texture)
        self.texture = self.idle_animation[0]
    
    def update_animation(self, delta_time):
        self.idle_texture += 1
        if self.idle_texture > (8 * AnimationSpeed) - 1:
            self.idle_texture = 0
        frame = self.idle_texture // AnimationSpeed
        self.texture = self.idle_animation[frame]

class Enemy(arcade.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        #Enemy initial states and trackers
        self.character_face_direction = FacingLeft
        self.health = 1
        self.is_attacked = False
        self.is_attacking = False
        self.attacked_direction = None
        self.initial_direction = randint(0,1)
        self.is_dead = False
        self.left_boundary = None
        self.right_boundary = None
        
        #Animation frames
        self.walk_texture = 0
        self.death_texture = 0

        #Loads the enemy textures
        assets = "Assets/Enemies/Enemy"

        self.walk_animation = []
        for i in range(7):
            texture = LoadTexturePair(f"{assets}Walk{i}.png")
            self.walk_animation.append(texture)
        
        self.death_animation = []
        for i in range(9):
            texture = LoadTexturePair(f"{assets}Death{i}.png")
            self.death_animation.append(texture)
        
        self.texture = self.walk_animation[0][self.character_face_direction]
        self.set_hit_box([[-30, -80], [30, -80], [30, 60], [-10, 60]])
    
    def searchPlayer(self):
        #When the enemy has line of sight with the player with the max distance being 300 pixels, the enemy is not being attacked and the player is not being attacked, they will move towards the player
        if arcade.has_line_of_sight(self.game.player_sprite.position, self.position, (self.game.invis_barriers), max_distance = 300) and not self.is_attacked and not self.game.player_sprite.is_attacked:
            if self.game.player_sprite.center_x < self.center_x:
                self.change_x = -1.75
            else:
                self.change_x = 1.75
        elif not self.is_attacked:
            if len(arcade.check_for_collision_with_list(self, self.game.invis_barriers)) > 0:
                self.change_x *= -1
            elif self.center_x < self.left_boundary:
                self.change_x = 0.75
            elif self.center_x > self.right_boundary:
                self.change_x = -0.75
                #If the enemy is attacking the player the enemy would stop for a moment
        if self.is_attacking:
            self.change_x = 0

    def update_animation(self, delta_time):
        if not self.is_attacked:
            if self.change_x < 0 and self.character_face_direction == FacingRight:
                self.character_face_direction = FacingLeft
            elif self.change_x > 0 and self.character_face_direction == FacingLeft:
                self.character_face_direction = FacingRight
                
        if not self.is_dead:
            self.walk_texture += 1
            if self.walk_texture > (7 *AnimationSpeed) - 1:
                self.walk_texture = 0
            frame = self.walk_texture // AnimationSpeed
            self.texture = self.walk_animation[frame][self.character_face_direction]
        else:
            self.death_texture += 1
            if self.death_texture > (9 * AnimationSpeed) - 1:
                self.death_texture = 8 * AnimationSpeed
            frame = self.death_texture // AnimationSpeed
            self.texture = self.death_animation[frame][self.character_face_direction]

class PlayerCharacter(arcade.Sprite):
    """Inherits the attribute from arcade.sprite. Used to store all of the animation for the player character"""
    def __init__(self):

        #Set up parent class
        super().__init__()

        #Player Initial states
        self.Health = 3
        self.character_face_direction = FacingRight
        self.change_x = 0

        #Texture frames
        self.idle_texture = 0
        self.running_texture = 0
        self.jumping_texture = 0
        self.attack_texture = 0

        #Track the player state
        self.attacked_direction = None
        self.jump_needs_reset = False
        self.is_jumping = False
        self.is_attacking = False
        self.is_attacked = False
        self.is_dead = False

        #Load the character's Textures

        assets = "Assets/PlayableCharacters/Player1"

        #Player's Sword Hitbox
        self.sword_hit_box = arcade.Sprite(f"Assets/PlayableCharacters/SwordHitBox.png")
        self.sword_hit_box.set_hit_box([[0,0], [48, 0], [48, 120], [0, 120]])

        #Load textures for idle animation
        self.idle_animation = []
        for i in range(8):
            texture = LoadTexturePair(f"{assets}Idle{i}.png")
            self.idle_animation.append(texture)

        #Load textures for the runnning animation
        self.running_animation = []
        for i in range(8):
            texture = LoadTexturePair(f"{assets}Running{i}.png")
            self.running_animation.append(texture)
        
        #Loads textures for the jumping / falling animation
        self.jumping_animation = []
        for i in range(2):
            texture = LoadTexturePair(f"{assets}Jump{i}.png")
            self.jumping_animation.append(texture)
        
        #Load attack animation
        self.attack_animation = []
        for i in range(5):
            texture = LoadTexturePair(f"{assets}Attack{i}.png")
            self.attack_animation.append(texture)

        #Set the texture when the player is spawned
        self.texture = self.idle_animation[0][0]

        #Sets the character hitbox with a list of x and y that create the hitbox.
        self.set_hit_box([[-31, -115], [30, -115], [15, 45], [-20, 45]])

    def update_animation(self, delta_time):
        '''
        Every 1/60 seconds this method is going to be called on the object
        '''
        #Figure out if we need to flip face left or right
        if not self.is_attacked:
            if self.change_x < 0 and self.character_face_direction == FacingRight:
                self.character_face_direction = FacingLeft
            elif self.change_x > 0 and self.character_face_direction == FacingLeft:
                self.character_face_direction = FacingRight
        if not self.is_dead:
            #Idle Animation
            if self.change_x == 0 and self.change_y == 0 and not self.is_attacking:
                self.idle_texture += 1
                if self.idle_texture > (8 * AnimationSpeed) -1:
                    self.idle_texture = 0
                frame = self.idle_texture // AnimationSpeed
                self.texture = self.idle_animation[frame][self.character_face_direction]
            
            #Running Animation
            if abs(self.change_x) > 0:
                self.running_texture += 1
                if self.running_texture > (8 * AnimationSpeed) - 1:
                    self.running_texture = 0
                frame = self.running_texture // AnimationSpeed
                self.texture = self.running_animation[frame][self.character_face_direction]
            
            #Jumping Animation
            if self.is_jumping:
                self.jumping_texture += 1
                if self.jumping_texture > (2 * AnimationSpeed) - 1:
                    self.jumping_texture = 0
                frame = self.jumping_texture // AnimationSpeed
                self.texture = self.jumping_animation[frame][self.character_face_direction]
            
            #Attack Animation
            if self.is_attacking:
                self.attack_texture += 1
                if self.attack_texture > 4 * AnimationSpeed:
                    self.idle_texture = 40
                    self.texture = self.idle_animation[self.idle_texture // AnimationSpeed][self.character_face_direction]
                    self.is_attacking = False
                    self.attack_texture = 0
                frame = self.attack_texture // AnimationSpeed
                self.texture = self.attack_animation[frame][self.character_face_direction]
        else:
            self.texture = self.jumping_animation[0][self.character_face_direction]

class ImageButton(arcade.gui.UIImageButton):
    def __init__(self, normal_texture, hovered_texture, pressed_texture, x, y):
        super().__init__(normal_texture = normal_texture, hover_texture = hovered_texture, press_texture = pressed_texture, center_x = x, center_y = y)
        self.is_clicked = False

    def on_click(self):
        self.is_clicked = True

#Start Menu Screen
class GameStart(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui_manager = UIManager()
        self.music = arcade.Sound("Assets/Audio/burn_no_autostart.wav")
    
    def on_show(self):
        self.current_music = self.music.play(loop = True)
        self.setup()
        arcade.set_background_color((22, 16, 70))

    def setup(self):
        self.window.set_viewport(0, 1000, 0, 650)
        self.window.set_mouse_visible(visible = True)
        self.ui_manager.purge_ui_elements()

        self.decor_list = arcade.SpriteList()

        decor = arcade.Sprite("Assets/UiStuff/GameStartTorch.png")
        newGame_button_normal = arcade.load_texture("Assets/UiStuff/NewGame0.png")
        newGame_button_hovered = arcade.load_texture("Assets/UiStuff/NewGame1.png")
        newGame_button_pressed = arcade.load_texture("Assets/UiStuff/NewGame0.png")
        quit_button_normal = arcade.load_texture("Assets/UiStuff/Quit0.png")
        quit_button_hovered = arcade.load_texture("Assets/UiStuff/Quit1.png")
        quit_button_pressed = arcade.load_texture("Assets/UiStuff/Quit0.png")

        decor.center_x = 500
        decor.center_y = 325
        self.decor_list.append(decor)

        self.NewGameButton = ImageButton(newGame_button_normal, newGame_button_hovered, newGame_button_pressed,  800, 325)
        self.QuitButton = ImageButton(quit_button_normal, quit_button_hovered, quit_button_pressed, 200, 325)
        self.ui_manager.add_ui_element(self.NewGameButton)
        self.ui_manager.add_ui_element(self.QuitButton)
    
    def on_update(self, delta_time):
        if self.NewGameButton.is_clicked == True:
            self.music.stop(self.current_music)
            self.ui_manager.purge_ui_elements()
            view = GameState()
            view.setup()
            self.window.show_view(view)
        if self.QuitButton.is_clicked == True:
            arcade.close_window()

    def on_draw(self):
        arcade.start_render()
        self.decor_list.draw()

#Game Over Screen
class GameOver(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui_manager = UIManager()

    def on_show(self):
        self.setup()
        arcade.set_background_color(arcade.color.BLACK)
    
    def setup(self):
        #resets the viewport otherwise the button hitbox may not be accurate
        self.window.set_viewport(0, 1000, 0, 650)
        #Set the mouse to be visible again
        self.window.set_mouse_visible(visible = True)
        #Reset all the gui element every time the setup is called to avoid misshandled ui elements
        self.ui_manager.purge_ui_elements()

        #initiate the sprite list
        self.decor_list = arcade.SpriteList()

        #Loads the texture
        decor = arcade.Sprite("Assets/UiStuff/GameOverSword.png")
        restart_button_normal = arcade.load_texture("Assets/UiStuff/Restart0.png")
        restart_button_hovered = arcade.load_texture("Assets/UiStuff/Restart1.png")
        restart_button_pressed = arcade.load_texture("Assets/UiStuff/Restart0.png")
        quit_button_normal = arcade.load_texture("Assets/UiStuff/GiveUp0.png")
        quit_button_hovered = arcade.load_texture("Assets/UiStuff/GiveUp1.png")
        quit_button_pressed = arcade.load_texture("Assets/UiStuff/GiveUp0.png")

        #Adds the texture to the sprite list and as the gui elements
        decor.center_x = 500
        decor.center_y = 325
        self.decor_list.append(decor)

        self.RestartButton = ImageButton(restart_button_normal, restart_button_hovered, restart_button_pressed,  800, 325)
        self.QuitButton = ImageButton(quit_button_normal, quit_button_hovered, quit_button_pressed, 200, 325)
        self.ui_manager.add_ui_element(self.RestartButton)
        self.ui_manager.add_ui_element(self.QuitButton)
    
    def on_update(self, delta_time):
        if self.RestartButton.is_clicked == True:
            self.ui_manager.purge_ui_elements()
            view = GameState()
            view.setup()
            self.window.show_view(view)
        if self.QuitButton.is_clicked == True:
            arcade.close_window()
    
    def on_draw(self):
        arcade.start_render()
        self.decor_list.draw()

#Pause Menu Screen
class PauseMenu(arcade.View):
    '''
    All of the processing of the assets and other stuff goes here
    '''
    def __init__(self, view, width0, width1, height0, height1):
        super().__init__()
        self.current_view = view
        self.width0 = width0
        self.width1 = width1
        self.height0 = height0
        self.height1 = height1
        self.ui_manager = UIManager()

    def on_show(self):
        self.setup()
        arcade.set_background_color((20, 16, 69))

    def setup(self):
        self.window.set_mouse_visible(visible = True)
        arcade.set_viewport(0, 1000, 0, 650)
        self.ui_manager.purge_ui_elements()
        
        self.decor_list = arcade.SpriteList()

        decor = arcade.Sprite("Assets/UiStuff/PauseMenuDecor.png")
        continue_button_normal = arcade.load_texture("Assets/UiStuff/Continue0.png")
        continue_button_hovered = arcade.load_texture("Assets/UiStuff/Continue1.png")
        continue_button_pressed = arcade.load_texture("Assets/UiStuff/Continue0.png")
        quit_button_normal = arcade.load_texture("Assets/UiStuff/Quit0.png")
        quit_button_hovered = arcade.load_texture("Assets/UiStuff/Quit1.png")
        quit_button_pressed = arcade.load_texture("Assets/UiStuff/Quit0.png")

        decor.center_x = 500
        decor.center_y = 325
        self.decor_list.append(decor)

        self.ContinueButton = ImageButton(continue_button_normal, continue_button_hovered, continue_button_pressed,  800, 325)
        self.QuitButton = ImageButton(quit_button_normal, quit_button_hovered, quit_button_pressed, 200, 325)
        self.ui_manager.add_ui_element(self.ContinueButton)
        self.ui_manager.add_ui_element(self.QuitButton)
    
    def on_key_press(self, key, modifiers):
        if arcade.key.ESCAPE:
            self.ui_manager.purge_ui_elements()
            view = self.current_view
            view.is_paused = False
            self.window.show_view(view)
            arcade.set_viewport(self.width0, self.width1, self.height0, self.height1)

    def on_update(self, delta_time):
        if self.ContinueButton.is_clicked == True:
            self.ui_manager.purge_ui_elements()
            view = self.current_view
            view.is_paused = False
            self.window.show_view(view)
            arcade.set_viewport(self.width0, self.width1, self.height0, self.height1)
        if self.QuitButton.is_clicked == True:
            arcade.close_window()

    def on_draw(self):
        arcade.start_render()
        self.decor_list.draw()

#Main Game screen
class GameState(arcade.View):
    """
    All of the processing of the assets and stuff goes here
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__()

        #Keep track of the file directory
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.game_over = False
        self.is_paused = False
        self.started = True

        #Going to be used when scrolling the screen
        self.view_bottom = 0
        self.view_left = 0

        #Trackers necessary for controlling the player
        self.attacked_direction = None
        self.A_pressed = False
        self.D_pressed = False
        self.Space_pressed = False
        self.Control_pressed = False
        self.left_mouse_pressed = False
        
        #Lists for all of the sprites
        self.player_list = None
        self.enemy_list = None
        self.health_ui = None
        self.transition_ui = None
        self.walls_list = None
        self.hit_boxes_list = None

        #Separate variable that holds the player sprite
        self.player_sprite = None

        #Physics that is going to be used 
        self.enemy_physics = None

    def setup(self):
        """ Set up the game here."""
        #initiate the the sprite lists
        self.walls_list = arcade.SpriteList()
        self.DeathFog_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.hit_boxes_list = arcade.SpriteList()
        self.health_ui = arcade.SpriteList()
        self.key_collectible_ui = arcade.SpriteList()
        self.collectible = arcade.SpriteList()
        self.invis_barriers = arcade.SpriteList()
        self.transition_ui = arcade.SpriteList()

        #Tracker for keys
        self.Game_finished = False
        self.collected_key = 0

        #Going to be used when scrolling the screen
        self.view_bottom = 0
        self.view_left = 0
        
        #Sounds
        self.enemy_death_sound = arcade.load_sound("Assets/Audio/ghost.wav")
        self.player_death_sound = arcade.load_sound("Assets/Audio/lose sound 1_0.wav")
        self.player_hurt = arcade.load_sound("Assets/Audio/cut_grunt2.wav")
        self.player_jump = arcade.load_sound("Assets/Audio/gruntsound.wav")
        self.PauseSound = arcade.load_sound("Assets/Audio/Menu A_select.wav")
        self.collect_key = arcade.load_sound("Assets/Audio/spell2.wav")
        self.music = arcade.Sound("Assets/Audio/lost.ogg")

        #Keys that serves as the collectible in the game
        coordinates = [[470, 1622], [3018, 462], [6335, 1050]]
        for coordinate in coordinates:
            keyCollectible = KeyCollectible()
            keyCollectible.position = coordinate
            self.collectible.append(keyCollectible)

        #EnemyBarriers to prevent them falling from an edge or keeps walking in front of a wall and as another wall preventing them from detecting the player
        coordinates = [[890, 1582], [2805, 940], [4210, 1000], [5810, 1000]]
    
        for coordinate in coordinates:
            invisBarrier = arcade.Sprite("Assets/Tiles/EnemyBarrier.png")
            invisBarrier.set_hit_box([[0,0], [12, 0], [12, 500], [0, 500]])
            invisBarrier.position = coordinate
            self.invis_barriers.append(invisBarrier)

        #Health bar for the ui
        self.health_ui_list = []
        for i in range(3):
            texture = arcade.Sprite(f"Assets/UiStuff/Health{i}.png")
            self.health_ui_list.append(texture)

        #Ui for the key
        self.key_ui = []
        for i in range(4):
            sprite = arcade.Sprite(f"Assets/UiStuff/KeyCollectibleUi{i}.png")
            self.key_ui.append(sprite)

        #Transition stuff
        self.transition_image = arcade.Sprite("Assets/UiStuff/Transition.png")
        self.transition_image_frame = 0

        #Spawn in a player character
        self.player_sprite = PlayerCharacter()

        self.player_sprite.center_x = 500
        self.player_sprite.center_y = 988
        self.player_list.append(self.player_sprite)

        #Enemies Spawn
        coordinates = [[704, 1592], [3000, 988], [4400, 1100], [6004, 1100]]
        for coordinate in coordinates:
            enemy = Enemy(self)
            enemy.position = coordinate
            enemy.left_boundary = enemy.center_x - 150
            enemy.right_boundary = enemy.center_x + 150
            if enemy.initial_direction == 0:
                enemy.change_x = 0.75
            else:
                enemy.change_x = -0.75
            self.enemy_list.append(enemy)

        #Load in the map from a tmx file
        #Name of map file to load
        map_name = "Assets/Maps/Level1.tmx"
        #The layer that contains impassable object 
        walls_layer_name = 'Walls'
        #The layer that contains insta death object
        death_fog_layer_name = 'DeathFog'

        #Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)

        #Walls
        self.walls_list = arcade.tilemap.process_layer(map_object = my_map,
                                                      layer_name = walls_layer_name,
                                                      use_spatial_hash = True)   

        #DeathFog
        self.DeathFog_list = arcade.tilemap.process_layer(map_object = my_map,
                                                          layer_name = death_fog_layer_name,
                                                          use_spatial_hash = True)

        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.walls_list,
                                                             gravity_constant = Gravity)
    
    def on_show(self):
        self.started = True
        self.current_music = self.music.play(loop = True)
        self.window.set_mouse_visible(visible=False)
        arcade.set_background_color((45, 0, 120))
          
    def on_key_press(self, key, modifiers):
        if key == arcade.key.D:
            self.D_pressed = True
        elif key == arcade.key.A:
            self.A_pressed = True
        elif key == arcade.key.SPACE:
            self.Space_pressed = True
        elif key == arcade.key.ESCAPE:
            if not self.is_paused:
                arcade.play_sound(self.PauseSound)
            self.is_paused = True
            self.D_pressed = False
            self.A_pressed = False
            self.Space_pressed = False
            self.left_mouse_pressed = False

    def on_key_release(self, key, modifiers):
        if key == arcade.key.D:
            self.D_pressed = False
        elif key == arcade.key.A:
            self.A_pressed = False
        elif key == arcade.key.SPACE:
            self.Space_pressed = False

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.left_mouse_pressed = True

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.left_mouse_pressed = False
    
    def on_update(self, delta_time):
        """
        Game Logic. Behave like a while True loop that loops every 1/60 seconds
        """
        #Track if we need to change the viewport
        changed = False

        #Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed = True

        #Scroll right
        right_boundary = self.view_left + ScreenWidth - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed = True

        #Scroll up
        top_boundary = self.view_bottom + ScreenHeight - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed = True

        #Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed = True

        if changed:
            #Convert the result to integers so we don't get some weird pixel lineup on the screen
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            #Change the viewport every 1/60 second to that of the data acquired
            arcade.set_viewport(self.view_left,
                                ScreenWidth + self.view_left,
                                self.view_bottom,
                                ScreenHeight + self.view_bottom)
        
        #Trackers for the key collectible
        for item in self.key_collectible_ui:
            self.key_collectible_ui.remove(item)
        
        #Show the collected key ui
        ScrollSprite(self.key_ui[self.collected_key], self.key_collectible_ui, 880, 60)
        
        #Checks if the collected key is equal to three. If it is the game is finished
        if self.collected_key >= 3:
            self.Game_finished = True

        #Trackers for the player health and changes the sprite needed to show the information of the player's health
        for item in self.health_ui:
            self.health_ui.remove(item)
        if self.player_sprite.Health <= 0:
            self.player_sprite.is_dead = True
            ScrollSprite(self.health_ui_list[0], self.health_ui, 100, 50)
        else:
            ScrollSprite(self.health_ui_list[self.player_sprite.Health - 1], self.health_ui, 100, 50)

        #Changes the state of the character depending on the conditions
        #When the player is on the ground, their state is going to be changed to not jumping and not being attacked
        if self.physics_engine.can_jump():
            self.player_sprite.is_jumping = False
            self.player_sprite.is_attacked = False
            for enemy in self.enemy_list:
                if enemy.is_attacking:
                    enemy.is_attacking = False
        #If they are not on the ground their state are going to be changed wether if they are attacked or not
        else:
            self.player_sprite.is_jumping = True
                                    
        #Launches the character automatically after they are attacked depending on the direction of the attacker
        if self.player_sprite.is_attacked:
            if self.player_sprite.attacked_direction == 1:
                self.player_sprite.change_x = -2
            else:
                self.player_sprite.change_x = 2
            
        #Player Control
        #Movement Control
        if not self.player_sprite.is_attacked and not self.player_sprite.is_dead:
            if self.Space_pressed and not self.player_sprite.is_attacking and self.physics_engine.can_jump():
                arcade.play_sound(self.player_jump)
                self.player_sprite.change_y = PlayerJumpSpeed
                self.player_sprite.is_jumping = True

            if self.A_pressed and not self.D_pressed and not self.player_sprite.is_attacking:
                self.player_sprite.change_x = -PlayerSpeed
            elif self.D_pressed and not self.A_pressed and not self.player_sprite.is_attacking:
                self.player_sprite.change_x = PlayerSpeed
            else:
                self.player_sprite.change_x = 0

            #Player Attack Control
            if self.left_mouse_pressed and not self.player_sprite.is_jumping and not self.player_sprite.is_attacking:
                self.player_sprite.is_attacking = True
                self.player_sprite.change_x = 0
                print(self.player_sprite.center_x)

        #Keep track the player location needed for spawning attack hitbox
        self.player_x = self.player_sprite._get_center_x()
        self.player_y = self.player_sprite._get_center_y() - 80
        
        #Remove keys when the player touches them
        hitted_list = arcade.check_for_collision_with_list(self.player_sprite, self.collectible)
        if len(hitted_list) > 0:
            for key in hitted_list:
                key.remove_from_sprite_lists()
                arcade.play_sound(self.collect_key)
                self.collected_key += 1
                print(self.collected_key)

        #Creates a hitbox when the character attacks depending on the character direction
        if self.player_sprite.is_attacking and self.player_sprite.attack_texture == 2 * AnimationSpeed:
            if self.player_sprite.character_face_direction == 0:
                self.player_sprite.sword_hit_box.center_x = self.player_x + 40
                self.player_sprite.sword_hit_box.center_y = self.player_y
                self.hit_boxes_list.append(self.player_sprite.sword_hit_box)
            elif self.player_sprite.character_face_direction == 1:               
                self.player_sprite.sword_hit_box.center_x = self.player_x - 90
                self.player_sprite.sword_hit_box.center_y = self.player_y
                self.hit_boxes_list.append(self.player_sprite.sword_hit_box)
        
        #Removes the hitbox after the character attack animation has reached above frame 4
        if self.player_sprite.attack_texture  == 4 * AnimationSpeed:
            for hit_boxes in self.hit_boxes_list:
                self.hit_boxes_list.remove(hit_boxes)
        
        #Instantly kills the player when they come in contact with a deathfog
        hitted_list = arcade.check_for_collision_with_list(self.player_sprite, self.DeathFog_list)
        if len(hitted_list) > 0:
            self.player_sprite.change_y = 0
            self.player_sprite.is_dead = True

        #Detect if the player was attacked by an enemy
        #Return the enemy that is in contact with the player's hitbox
        hitted_list = arcade.check_for_collision_with_list(self.player_sprite, self.enemy_list)
        for enemy in hitted_list:
            #Only process it if the enemy is still alive to prevent damaging the player when the enemy's health is already below zero
            #launches the player depending on the enemy position relative to the player upon impact
            if not enemy.is_dead:
                enemy.is_attacking = True
                if not self.player_sprite.is_attacked and not enemy.is_attacked:
                    arcade.play_sound(self.player_hurt)
                    self.player_sprite.Health -= 1
                    self.player_sprite.change_y = 8
                    self.player_sprite.is_attacked = True
                    if enemy.center_x > self.player_sprite.center_x:
                        self.player_sprite.change_x = -5
                        self.player_sprite.attacked_direction = 1
                    if enemy.center_x < self.player_sprite.center_x: 
                        self.player_sprite.change_x = 5
                        self.player_sprite.attacked_direction = 0
                    else:
                        self.player_sprite.change_x = -5
                        self.player_sprite.attacked_direction = 1
        
        #This is separated to prevent overplaying the enemy death sound
        for enemy in self.enemy_list:
            #Checks wether the enemy is on the ground. since when an enemy is never on the ground after they get attacked the attribute is gonna be changed only if they are on the ground
            if arcade.PhysicsEnginePlatformer(enemy, self.walls_list, gravity_constant = Gravity).can_jump():
                enemy.is_attacked = False

        #Detect if an enemy was hit by the player's sword
        for attacks in self.hit_boxes_list:
            #Returns the enemy object that is on collision with the player's attack hitbox
            hit_list = arcade.check_for_collision_with_list(attacks, self.enemy_list)
            for enemy in hit_list:
                #Only process it for the enemy that is not in the state of being attacked to prevent over damaging the enemy
                #Launches the enemy depending on the attack direction
                if not enemy.is_attacked and not enemy.is_dead:
                    arcade.play_sound(self.enemy_death_sound)
                    enemy.health -= 1
                    enemy.change_y = 6
                    enemy.is_attacked = True
                    if enemy.center_x > self.player_sprite.center_x:
                        enemy.change_x = 2
                        enemy.attacked_direction = 0
                    elif enemy.center_x < self.player_sprite.center_x:
                        enemy.change_x = -2
                        enemy.attacked_direction = 1
                        
        #Adds a transition effect before going to the game over view or pause menu view
        #Resets the list every call
        for item in self.transition_ui:
            self.transition_ui.remove(item)

        #Creates the transition effect for going to the game over screen and the pause screen
        if self.player_sprite.is_dead or self.is_paused or self.Game_finished:
            self.transition_image_frame += 1
            #When the animation is finished, check if the player is dead, game is paused, or game is finished.
            if self.transition_image_frame == 4 * AnimationSpeed:
                #If the players is dead, go to the game over screen
                if self.player_sprite.is_dead:
                    self.transition_image_frame = 0
                    view = GameOver()
                    self.window.show_view(view)
                #if the game is paused go to the pause screen
                elif self.is_paused:
                    self.transition_image_frame = 0
                    self.music.stop(player = self.current_music)
                    view = PauseMenu(self, arcade.get_viewport()[0], arcade.get_viewport()[1], arcade.get_viewport()[2], arcade.get_viewport()[3])
                    self.window.show_view(view)
                #if the game is finished go to the end screen
                elif self.Game_finished:
                    self.transition_image_frame = 0
                    self.music.stop(player = self.current_music)
                    view = GameEnd()
                    self.window.show_view(view)
            #Gradually change the coordinate of a black box that is going to cover the screen
            self.transition_image.center_x = arcade.get_viewport()[0] + 500
            self.transition_image.center_y = arcade.get_viewport()[3] - ((self.transition_image_frame // AnimationSpeed) * 82)
            self.transition_ui.append(self.transition_image)
        #Updates the old list to the new list
        
        #Adds the transition effect at the start of the game also
        if self.started:
            #Gradually moves a black box that is covering the screen to be outside of the screen
            self.transition_image.center_x = arcade.get_viewport()[0] + 500
            self.transition_image.center_y = (arcade.get_viewport()[3] - 325) +  (((self.transition_image_frame // AnimationSpeed) * 82))
            self.transition_ui.append(self.transition_image)
            self.transition_image_frame += 1
            if self.transition_image_frame > 4 * AnimationSpeed:
                self.started = False
                self.transition_image_frame = 4 * AnimationSpeed
        
        #When the player is dead play a death sound and stop the current music then remove the player from the sprite list
        if self.player_sprite.is_dead:
            if len(self.player_list) > 0:
                arcade.play_sound(self.player_death_sound)
                self.music.stop(player = self.current_music)
            self.player_sprite.remove_from_sprite_lists()

        #Update the Enemies
        for enemy in self.enemy_list:
            #The enemy would automatically get launched and pushed depending on the direction they are attacked.
            if enemy.is_attacked:
                if enemy.attacked_direction == 1:
                    enemy.change_x = -2
                else:
                    enemy.change_x = 2
            #The enemy 'AI' is going to be running whenever the enemy is not dead
            if not enemy.is_dead:
                enemy.searchPlayer()
            #Updates the enemy according to the game's physics
            arcade.PhysicsEnginePlatformer(enemy, self.walls_list, gravity_constant = Gravity).update()
            #Upddates the enemy animation
            enemy.update_animation(delta_time)
            #Kills the enemy if they touches the deathfog
            if len(arcade.check_for_collision_with_list(enemy, self.DeathFog_list)) > 0:
                enemy.change_y = 0
                enemy.is_dead = True
            #Kills the enemy when their health reaches zero
            if enemy.health <= 0 and enemy.change_y == 0:
                enemy.change_x = 0
                if arcade.PhysicsEnginePlatformer(enemy, self.walls_list, gravity_constant = Gravity).can_jump():
                    enemy.is_dead = True
            #Gradually decreases the enemy opacity after their death animation is finished until they become invisible and then remove them from the game
            if enemy.death_texture > (8 * AnimationSpeed) - 1:
                enemy.alpha -= 15
                if enemy.alpha <= 0:
                    self.enemy_list.remove(enemy)
        
        #Updates the player animation and location based on the physics engine
        self.physics_engine.update()
        self.player_sprite.update_animation(delta_time)
        
        #Playes the key animation
        for key in self.collectible:
            key.update_animation(delta_time)
   
        #Resets back the frame counter to zero for the case of the starting transition
        if self.transition_image_frame == (4 * AnimationSpeed) and not self.started:
            self.transition_image_frame = 0

    def on_draw(self):
        """ Render the screen. """

        arcade.start_render()
        self.walls_list.draw()
        self.enemy_list.draw()
        self.player_list.draw()
        self.DeathFog_list.draw()
        self.collectible.draw()
        self.key_collectible_ui.draw()
        self.health_ui.draw()
        self.hit_boxes_list.draw()
        self.invis_barriers.draw()
        self.transition_ui.draw()
        #Debug Stuff
        """ self.enemy_list.draw_hit_boxes()
        self.player_sprite.draw_hit_box()
        self.hit_boxes_list.draw_hit_boxes()
        self.invis_barriers.draw_hit_boxes()
        self.collectible.draw_hit_boxes() """

#Game End Screen
class GameEnd(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui_manager = UIManager()

    def on_show(self):
        self.setup()
        arcade.set_background_color((10, 7, 38))
    
    def setup(self):
        self.window.set_viewport(0, 1000, 0, 650)
        self.window.set_mouse_visible(visible = True)
        self.ui_manager.purge_ui_elements()

        self.decor_list = arcade.SpriteList()

        decor = arcade.Sprite("Assets/UiStuff/EndScreenDecor.png")
        retry_button_normal = arcade.load_texture("Assets/UiStuff/Retry0.png")
        retry_button_hovered = arcade.load_texture("Assets/UiStuff/Retry1.png")
        retry_button_pressed = arcade.load_texture("Assets/UiStuff/Retry1.png")
        exit_button_normal = arcade.load_texture("Assets/UiStuff/Exit0.png")
        exit_button_hovered = arcade.load_texture("Assets/UiStuff/Exit1.png")
        exit_button_pressed = arcade.load_texture("Assets/UiStuff/Exit1.png")

        decor.center_x = 500
        decor.center_y = 325
        self.decor_list.append(decor)

        self.ExitButton = ImageButton(exit_button_normal, exit_button_hovered, exit_button_pressed,  800, 325)
        self.RestartButton = ImageButton(retry_button_normal, retry_button_hovered, retry_button_pressed, 200, 325)
        self.ui_manager.add_ui_element(self.ExitButton)
        self.ui_manager.add_ui_element(self.RestartButton)
    
    def on_draw(self):
        arcade.start_render()
        self.decor_list.draw()
    
    def on_update(self, delta_time):
        if self.ExitButton.is_clicked:
            arcade.close_window()
        if self.RestartButton.is_clicked:
            self.ui_manager.purge_ui_elements()
            view = GameStart()
            self.window.show_view(view)

#Data that is going to be used to process the game application window.
ScreenWidth = 1000
ScreenHeight = 650
ScreenTitle = "ANIMO"

#How many pixels to keep as a minimum margin between the character and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 300
RIGHT_VIEWPORT_MARGIN = 600
BOTTOM_VIEWPORT_MARGIN = 200
TOP_VIEWPORT_MARGIN = 400

#Physics of the game in pixels per frame.
PlayerSpeed = 3.5
PlayerJumpSpeed = 15
AnimationSpeed = 7
Gravity = 0.5

#Going to be used in the character frame list to determine which texture is going to be loaded depending on the player direction.
FacingRight = 0
FacingLeft = 1

def main():
    """ Main method """
    window = arcade.Window(ScreenWidth, ScreenHeight, ScreenTitle)
    initialState = GameStart()
    window.show_view(initialState)
    arcade.run()

if __name__ == "__main__":
    main()