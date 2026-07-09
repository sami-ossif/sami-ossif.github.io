import pygame
from projectile import Projectile
#classe pour le personnage freezer
class Freezer(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.pv=200
        self.px_max=200
        self.attaque=16
        self.vitesse=16
        self.ki = 5
        self.ki_max = 20
        self.all_projectiles = pygame.sprite.Group()
        self.imageg = pygame.image.load('Image/Personnage/FriezaFF2.png').convert_alpha()
        self.imaged = pygame.image.load('Image/Personnage/FriezaFF1.png').convert_alpha()
        self.rect = self.imaged.get_rect()
        self.rect.x=1050
        self.rect.y= 450
        self.direction = -1
        self.is_jumping = False
        self.y_velocity = 0
        self.jump_speed =-28
        self.gravity = 1.5
        self.ground_y = 450
        self.blocking = False
        self.can_block = True
        self.block_cooldown = 500  # cooldown en millisecondes (0.5s)
        self.last_block_time = 0
        self.can_shoot = True
        self.shoot_cooldown = 600  # en millisecondes (1 seconde)
        self.last_shoot_time = 0
        self.can_strike = True
        self.strike_cooldown = 300  # 1 seconde
        self.last_strike_time = 0
        self.strike_image = pygame.image.load("Image/attaque/Strike.png")
        self.strike_active = False
        self.strike_start_time = 0





    def blast_freezer(self):
        current_time = pygame.time.get_ticks()
        if self.can_shoot and self.ki >= 1:
            self.all_projectiles.add(Projectile(self, self.direction))
            self.ki -= 1
            self.can_shoot = False
            self.last_shoot_time = current_time
        elif self.ki < 1:
            print("Pas de ki !")



    def charge_ki(self):
        if self.ki < self.ki_max:
            self.ki +=1
        self.charging = True

    def stop_charging(self):
        self.charging = False

    def strike_freezer(self, target):
        current_time = pygame.time.get_ticks()
        if self.can_strike:
            if self.rect.colliderect(target.rect):
                if not target.blocking:
                    target.pv -= 10  # Dégât de base
                else:
                    print("Attaque bloquée !")
            self.can_strike = False
            self.last_strike_time = current_time


    def start_block(self):
        current_time = pygame.time.get_ticks()
        if self.can_block and not self.blocking:
            self.blocking = True
            self.can_block = False
            self.last_block_time = current_time

    def stop_block(self):
        self.blocking = False

    def move_rightF(self):
        self.rect.x += self.vitesse

    def move_leftF(self):
        self.rect.x -= self.vitesse

    def sauter(self):
        global y_velocity, is_jumping
        if not self.is_jumping:
            self.y_velocity =self.jump_speed
            self.is_jumping = True

    def dessiner(self,screen):
        if self.direction == -1:
            self.image = self.imageg
        else:
            self.image = self.imaged

        screen.blit(self.image, self.rect)
        if self.blocking:
            pygame.draw.rect(screen, (255, 0, 0), self.rect, 3)

