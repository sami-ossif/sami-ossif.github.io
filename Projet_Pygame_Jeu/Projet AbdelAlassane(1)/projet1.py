import game
import pygame


pygame.init()


#generer la fenetre du jeu pygame
pygame.display.set_caption("Jeu Video")
#dimension
screen = pygame.display.set_mode((1200, 750))

#initialisation
pygame.key.set_repeat(1,300)
clock = pygame.time.Clock()

#Chargement des images
background = pygame.image.load('Image/Background/namek.jpg')#lien fichier de l'img

#charger notre jeu
jeu = game.Game()


running = True

def afficher_ecran_accueil(screen):
    # Charger le fond de l'écran d'accueil
    accueil_bg = pygame.image.load('Image/Background/ecran_accueil.jpg')  # <-- à personnaliser
    accueil_bg = pygame.transform.scale(accueil_bg, (1200, 750))

    # Police
    font_titre = pygame.font.Font(None, 80)
    font_texte = pygame.font.Font(None, 40)

    titre = font_titre.render("Bienvenue dans DBZ Fighters", True, (255, 255, 0))
    sous_titre = font_texte.render("Appuie sur une touche pour commencer", True, (255, 255, 255))

    screen.blit(accueil_bg, (0, 0))
    screen.blit(titre, (300, 200))
    screen.blit(sous_titre, (350, 400))
    pygame.display.flip()

    attendre_lancement()

def attendre_lancement():
    attente = True
    while attente:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                attente = False

def afficher_victoire_image(screen, gagnant):
    if gagnant == "Goku":
        fond = pygame.image.load("Image/Background/Goku_WW.jpeg")
    else:
        fond = pygame.image.load("Image/Background/Freezer_W.jpg")

    fond = pygame.transform.scale(fond, (1200, 750))

    # Charger la police personnalisée
    font = pygame.font.Font("PoliceTexte/W_font.otf", 80)

    texte = font.render(f"VICTOIRE DE {gagnant}", True, (255, 255, 255))

    screen.blit(fond, (0, 0))
    screen.blit(texte, (300, 50))
    pygame.display.flip()
    pygame.time.delay(4000)  # Affiche 4 secondes




#Boucle
while running:

    clock.tick(60)
    for event in pygame.event.get():
        #si le joueur ferme la fenetre
        if event.type == pygame.QUIT:
            running = False
        #si le joueur appuie sur une touche
        if event.type == pygame.KEYDOWN:
            jeu.pressed[event.key] = True
            #goku lance une kikoha
            if event.key == pygame.K_f:
                jeu.goku.blast_goku()
            #freezer lance une kikoha
            if event.key == pygame.K_KP2:
                jeu.freezer.blast_freezer()
            #goku charge son ki
            if event.key == pygame.K_r:
                jeu.goku.charge_ki()
            #freezer charge son ki
            if event.key == pygame.K_KP0:
                jeu.freezer.charge_ki()
            #Goku bloque
            if event.key == pygame.K_s:
                jeu.goku.start_block()
            #Freezer bloque
            if event.key == pygame.K_DOWN:
                jeu.freezer.start_block()
            # Goku attaque physique
            if event.key == pygame.K_g:
                jeu.goku.strike_goku(jeu.freezer)
                jeu.goku.strike_active = True
                jeu.goku.strike_start_time = pygame.time.get_ticks()
            # Freezer attaque physique
            if event.key == pygame.K_KP1:
                jeu.freezer.strike_freezer(jeu.goku)
                jeu.freezer.strike_active = True
                jeu.freezer.strike_start_time = pygame.time.get_ticks()



        #si le joueur relache une touche
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_s:
                jeu.goku.stop_block()

            if event.key == pygame.K_DOWN:
                jeu.freezer.stop_block()


    current_time = pygame.time.get_ticks()

    # Goku cooldown
    if not jeu.goku.can_block:
        if current_time - jeu.goku.last_block_time >= jeu.goku.block_cooldown:
            jeu.goku.can_block = True
    # Cooldown pour kikoha Goku
    if not jeu.goku.can_shoot:
        if current_time - jeu.goku.last_shoot_time >= jeu.goku.shoot_cooldown:
            jeu.goku.can_shoot = True
    # Goku strike cooldown
    if not jeu.goku.can_strike:
        if current_time - jeu.goku.last_strike_time >= jeu.goku.strike_cooldown:
            jeu.goku.can_strike = True


    # Freezer cooldown
    if not jeu.freezer.can_block:
        if current_time - jeu.freezer.last_block_time >= jeu.freezer.block_cooldown:
            jeu.freezer.can_block = True
    # Cooldown pour kikoha Freezer
    if not jeu.freezer.can_shoot:
        if current_time - jeu.freezer.last_shoot_time >= jeu.freezer.shoot_cooldown:
            jeu.freezer.can_shoot = True
    # Freezer strike cooldown
    if not jeu.freezer.can_strike:
        if current_time - jeu.freezer.last_strike_time >= jeu.freezer.strike_cooldown:
            jeu.freezer.can_strike = True


    def draw_health_bar(screen, x, y, current_health, max_health, couleur_barre):
        bar_width = 300
        bar_height = 25
        fill = (current_health / max_health) * bar_width
        outline_rect = pygame.Rect(x, y, bar_width, bar_height)
        fill_rect = pygame.Rect(x, y, fill, bar_height)

        pygame.draw.rect(screen, couleur_barre, fill_rect)
        pygame.draw.rect(screen, (255, 255, 255), outline_rect, 2)  # contour blanc


#Mouv. Goku
    key_pressed = pygame.key.get_pressed()
    if not jeu.goku.blocking:
        if key_pressed[pygame.K_a]:
            jeu.goku.move_leftG()
        if key_pressed[pygame.K_d]:
            jeu.goku.move_rightG()
        if key_pressed[pygame.K_w]:
            jeu.goku.sauter()

#Mouv. Freezer
    key_pressed = pygame.key.get_pressed()
    if not jeu.freezer.blocking:
        if key_pressed[pygame.K_LEFT]:
            jeu.freezer.move_leftF()
        if key_pressed[pygame.K_RIGHT]:
            jeu.freezer.move_rightF()
        if key_pressed[pygame.K_UP]:
            jeu.freezer.sauter()

#Collision Goku
    if jeu.goku.rect.x<10:
        jeu.goku.move_rightG()
    if jeu.goku.rect.x>1030:
        jeu.goku.move_leftG()

#collision Freezer
    if jeu.freezer.rect.x<0:
        jeu.freezer.move_rightF()
    if jeu.freezer.rect.x>1000:
        jeu.freezer.move_leftF()



    #retourner personnage
    if jeu.goku.rect.x > jeu.freezer.rect.x :
        jeu.goku.direction    =-1
        jeu.freezer.direction = 1
    elif jeu.goku.rect.x < jeu.freezer.rect.x :
        jeu.goku.direction    = 1
        jeu.freezer.direction =-1

    #Fair sauter Goku et Freezer
    jeu.goku.y_velocity += jeu.goku.gravity
    jeu.goku.rect.y += jeu.goku.y_velocity
    if jeu.goku.rect.y > 450 :
        jeu.goku.rect.y = 450
        jeu.goku.is_jumping = False

    jeu.freezer.y_velocity += jeu.freezer.gravity
    jeu.freezer.rect.y += jeu.freezer.y_velocity
    if jeu.freezer.rect.y > 450 :
        jeu.freezer.rect.y = 450
        jeu.freezer.is_jumping = False

    #Afficher le ki de Goku
    font = pygame.font.Font(None, 36)
    ki_text = font.render(f"Ki Goku: {jeu.goku.ki}", True, (0,0,255))
    #Afficher le ki Freezer
    ki_freezer_text = font.render(f"Ki Freezer: {jeu.freezer.ki}", True, (128, 0, 128))

    screen.blit(background,(00,00))
    # Afficher la barre de vie de Goku (à gauche)
    draw_health_bar(screen, 50, 50, jeu.goku.pv, jeu.goku.px_max, (0, 255, 0))

# Afficher la barre de vie de Freezer (à droite)
    draw_health_bar(screen, 850, 50, jeu.freezer.pv, jeu.freezer.px_max, (255, 0, 0))

    screen.blit(ki_freezer_text, (950, 10))
    screen.blit(ki_text, (10,10))
    #appliquer une image de mon joueur
    jeu.goku.dessiner(screen)

    jeu.freezer.dessiner(screen)
    #screen.blit(jeu.freezer.image, jeu.freezer.rect)

    for projectile in jeu.goku.all_projectiles:
        projectile.move()
    jeu.goku.all_projectiles.draw(screen)

    for projectile in jeu.freezer.all_projectiles:
        projectile.move()
    jeu.freezer.all_projectiles.draw(screen)

    # Collision projectiles Goku → Freezer
    for projectile in jeu.goku.all_projectiles:
        projectile.move()
        # Détection collision Freezer
        if projectile.rect.colliderect(jeu.freezer.rect):
            if jeu.freezer.blocking:
                # Blocage : réduire ou annuler les dégâts
                jeu.freezer.pv -= projectile.dmg // 3  # Par ex. dégâts divisés par 3
            else:
                jeu.freezer.pv -= projectile.dmg
            projectile.supprimer()

    # Collision projectiles Freezer → Goku
    for projectile in jeu.freezer.all_projectiles:
        projectile.move()
        # Détection collision Goku
        if projectile.rect.colliderect(jeu.goku.rect):
            if jeu.goku.blocking:
                jeu.goku.pv -= projectile.dmg // 3
            else:
                jeu.goku.pv -= projectile.dmg
            projectile.supprimer()

    # Vérifier si un joueur a perdu
    if jeu.goku.pv <= 0:
        afficher_victoire_image(screen, "Freezer")
        running = False

    if jeu.freezer.pv <= 0:
        afficher_victoire_image(screen, "Goku")
        running = False

    # Afficher attaque physique Goku
    if jeu.goku.strike_active and current_time - jeu.goku.strike_start_time <= 300:
        x = jeu.goku.rect.x + 60 * jeu.goku.direction
        y = jeu.goku.rect.y + 30
        screen.blit(jeu.goku.strike_image, (x+ 100, y + 30))
    else:
        jeu.goku.strike_active = False

    # Afficher attaque physique Freezer
    if jeu.freezer.strike_active and current_time - jeu.freezer.strike_start_time <= 300:
        x = jeu.freezer.rect.x + 60 * jeu.freezer.direction
        y = jeu.freezer.rect.y + 30
        screen.blit(jeu.freezer.strike_image, (x, y))
    else:
        jeu.freezer.strike_active = False





    pygame.display.flip()






pygame.quit()