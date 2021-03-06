import sys
import pygame
from bullet import Bullet
from alien import Alien
from time import sleep 

def check_keydown_events(event, ai_settings, screen, ship, bullets):
    """Respond to keypresses."""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_settings, screen, ship, bullets)
    elif event.key == pygame.K_q:
        sys.exit()        
        
def check_keyup_events(event, ship):
    """Respond to key releases."""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False

def check_events(ai_settings, screen, stats, sb, start_button, ship, aliens, bullets):
    """Respond to keypresses and mouse events."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, ship, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_start_button(ai_settings, screen, stats, sb, start_button, ship, aliens, bullets, mouse_x, mouse_y)
            
def check_start_button(ai_settings, screen, stats, sb, start_button, ship, aliens, bullets, mouse_x, mouse_y):
    """Start new game when start is clicked"""
    if start_button.rect.collidepoint(mouse_x, mouse_y):
        button_clicked = start_button.rect.collidepoint(mouse_x, mouse_y)
        if button_clicked and not stats.game_active:
            #Reset the game settings to defaults
            ai_settings.initialize_dynamic_settings()

            #Hide cursor
            pygame.mouse.set_visible(False)

            #Reset game stats
            stats.reset_stats()
            stats.game_active = True

            #Reset scoreboard images
            sb.prep_score()
            sb.prep_high_score()
            sb.prep_level()
            sb.prep_ships()

            #Empty all lists
            aliens.empty()
            bullets.empty()

            #Create a new fleet and center the ship
            create_fleet(ai_settings, screen, ship, aliens)
            ship.center_ship()
        
def fire_bullet(ai_settings, screen, ship, bullets):
    """Fire a bullet, if limit not reached yet."""
    # Create a new bullet, add to bullets group.
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)

def update_screen(ai_settings, screen, stats, sb,  ship, aliens, bullets, start_button):
    """Update images on the screen, and flip to the new screen."""
    # Redraw the screen, each pass through the loop.
    screen.fill(ai_settings.bg_color)
    
    # Redraw all bullets, behind ship and aliens.
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    ship.blitme()
    aliens.draw(screen)

    #Draw the scoreboard
    sb.show_score()

    #Draw the start button when inactive
    if not stats.game_active:
        start_button.draw_button()
    
    # Make the most recently drawn screen visible.
    pygame.display.flip()

def check_high_scores(stats, sb):
    """Check to see if New High Score"""
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()
    
def update_bullets(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """Update position of bullets, and get rid of old bullets."""
    # Update bullet positions.
    bullets.update()

    # Get rid of bullets that have disappeared.
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)

    check_bullet_alien_collision(ai_settings, screen, stats, sb, ship, aliens, bullets)

def check_bullet_alien_collision(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """Responds to bullet and alien colliosions"""
    #Remove any bullets and aliens that have colided, then speed up the game.
    collisions =  pygame.sprite.groupcollide(bullets, aliens, True, True)
    if collisions:
        for aliens in collisions.values():
            stats.score += ai_settings.alien_points * len(aliens)
            sb.prep_score()
        check_high_scores(stats, sb)
        
    if len(aliens) == 0:
        #Destroy existing bullets, create new fleet, level up, and speed up
        bullets.empty()
        ai_settings.increase_speed()

        #Increase level
        stats.level += 1
        sb.prep_level()

        create_fleet(ai_settings, screen, ship, aliens)

def get_number_aliens_x(ai_settings, alien_width):
    #find out limit per row
    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x/(2 * alien_width))
    return number_aliens_x

def get_number_rows(ai_settings, ship_height, alien_height):
    """Determine number of rows in the screen"""
    available_space_y = (ai_settings.screen_height - (3 * alien_height) - ship_height)
    number_rows = int(available_space_y / (2*alien_height))
    return number_rows

def create_alien(ai_settings, screen, aliens, alien_number, row_number):
    """Create an alien"""
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)

def create_fleet(ai_settings, screen, ship, aliens):
    """create a full fleet"""
    #Create aliens and find how many fit
    alien = Alien(ai_settings, screen)
    number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height, alien.rect.height)


    #Create first row
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            #Create an alien and place it in the row
            create_alien(ai_settings, screen, aliens, alien_number, row_number)

def check_fleet_edges(ai_settings, aliens):
    """Responds to aliens edge flags"""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break

def change_fleet_direction(ai_settings, aliens):
    """Drop the entire fleet 1 row and change directions"""
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1


def check_aliens_bottom(ai_settings, stats, screen, sb, ship, aliens, bullets):
    """check if any aliens hit the bottom"""
    screen_rect  = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            #Treat like ship hit
            ship_hit(ai_settings, stats, screen, sb, ship, aliens, bullets)
            break

def update_aliens(ai_settings, stats, screen, sb,  ship, aliens, bullets):
    """Update alien fleet"""
    check_fleet_edges(ai_settings, aliens)
    aliens.update()

    #Look for alien collision with the ship
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, stats, screen, sb, ship, aliens, bullets)
        print ("Ship Down!!!")

    #Look for aliens hitting the bottom
    check_aliens_bottom(ai_settings, stats, screen, sb, ship, aliens, bullets)

def ship_hit(ai_settings, stats, screen, sb,  ship, aliens, bullets):
    """Responds to ship alien impact"""
    #Reduce ships left
    if stats.ships_left > 0:
        stats.ships_left -= 1

        #Update Scoreboard
        sb.prep_ships()

        #Empty the list of aliens and bullets
        aliens.empty()
        bullets.empty()

        #Create a new fleet and recenter the ship
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()

        #Pause
        sleep(0.5)
    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)
 

