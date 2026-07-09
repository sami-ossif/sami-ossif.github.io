import pygame

#classe qui gere le projectile

class Projectile(pygame.sprite.Sprite):
    def __init__(self, lanceur, direction):
        super().__init__()
        self.vitesse = 10
        self.lanceur = lanceur
        self.dmg = lanceur.attaque
        if lanceur.__class__.__name__ == "Goku":
            self.image = pygame.image.load('Image/attaque/Kikoha.png')
        else:
            self.image = pygame.image.load('Image/attaque/DeathBall.png')
        self.image = pygame.transform.scale(self.image, (75, 75))
        self.rect = self.image.get_rect()
        self.rect.x = lanceur.rect.x + 100
        self.rect.y = lanceur.rect.y + 80
        self.direction = direction


    def supprimer(self):
        self.lanceur.all_projectiles.remove(self)

    def move(self):
        self.rect.x+= self.direction*self.vitesse
        if self.rect.x > 1200 or self.rect.x <0 :
            self.supprimer()