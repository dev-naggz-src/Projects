#!/usr/bin/env python3
"""
Space Invaders Game - Complete Implementation
A single-file Space Invaders-style game using Python and Pygame
"""

import pygame
import random
import math

# Game Setup & Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Game settings
PLAYER_SPEED = 5
BULLET_SPEED = 7
ALIEN_SPEED = 1
ALIEN_DROP = 20
ALIEN_ROWS = 5
ALIEN_COLS = 10
ALIEN_WIDTH = 40
ALIEN_HEIGHT = 30
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 30
BULLET_WIDTH = 3
BULLET_HEIGHT = 10

class Player(pygame.sprite.Sprite):
    """Represents the player's ship"""
    
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([PLAYER_WIDTH, PLAYER_HEIGHT])
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT - PLAYER_HEIGHT - 10
        self.speed = PLAYER_SPEED
        self.bullets = []  # List to track multiple bullets
        self.max_bullets = 2  # Maximum bullets allowed on screen
    
    def update(self, keys):
        """Update player position based on key presses"""
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
    
    def shoot(self):
        """Create and return a new bullet"""
        if len(self.bullets) < self.max_bullets:
            bullet = Bullet(self.rect.centerx, self.rect.top, -1)
            self.bullets.append(bullet)
            return bullet
        return None

class Alien(pygame.sprite.Sprite):
    """Represents a single alien enemy"""
    
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([ALIEN_WIDTH, ALIEN_HEIGHT])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1  # 1 for right, -1 for left
        self.last_shot = 0
        self.shot_delay = random.randint(2000, 5000)  # Longer delay between shots
    
    def update(self, current_time, speed):
        """Update alien position"""
        self.rect.x += speed * self.direction
    
    def should_shoot(self, current_time):
        """Check if alien should shoot"""
        if current_time - self.last_shot > self.shot_delay:
            self.last_shot = current_time
            self.shot_delay = random.randint(2000, 5000)
            return True
        return False

class Bullet(pygame.sprite.Sprite):
    """Represents a projectile"""
    
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface([BULLET_WIDTH, BULLET_HEIGHT])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x - BULLET_WIDTH // 2
        self.rect.y = y
        self.direction = direction  # -1 for up, 1 for down
        self.speed = BULLET_SPEED
    
    def update(self):
        """Update bullet position"""
        self.rect.y += self.speed * self.direction
        
        # Remove bullet if it goes off screen
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()
            return True  # Signal that bullet was destroyed
        return False

def setup_aliens():
    """Create and return a group of aliens in a grid formation"""
    aliens = pygame.sprite.Group()
    
    for row in range(ALIEN_ROWS):
        for col in range(ALIEN_COLS):
            x = col * (ALIEN_WIDTH + 10) + 50
            y = row * (ALIEN_HEIGHT + 10) + 50
            alien = Alien(x, y)
            aliens.add(alien)
    
    return aliens

def check_collisions(player, player_bullets, alien_bullets, aliens, score):
    """Check for collisions between game objects"""
    # Player bullets hitting aliens
    for bullet in player_bullets:
        alien_hit = pygame.sprite.spritecollideany(bullet, aliens)
        if alien_hit:
            bullet.kill()
            alien_hit.kill()
            score += 10
            # Remove the bullet from player's bullet list
            if bullet in player.bullets:
                player.bullets.remove(bullet)
    
    # Alien bullets hitting player
    for bullet in alien_bullets:
        if pygame.sprite.collide_rect(bullet, player):
            bullet.kill()
            return True, score  # Player hit, return updated score
    
    return False, score  # No player hit, return updated score

def draw_ui(screen, score, lives, font):
    """Draw the UI elements (score and lives)"""
    # Draw score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    # Draw lives
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 10, 10))

def draw_game_over(screen, message, font):
    """Draw game over or win message"""
    text = font.render(message, True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text, text_rect)

def main():
    """Main game function"""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Space Invaders")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    # Game state
    player = Player()
    aliens = setup_aliens()
    player_bullets = pygame.sprite.Group()
    alien_bullets = pygame.sprite.Group()
    
    # Game variables
    score = 0
    lives = 3
    alien_speed = ALIEN_SPEED
    game_over = False
    win = False
    
    # Timing
    last_alien_shot = 0
    alien_shot_delay = 1000  # milliseconds
    global_alien_shot_cooldown = 500  # Minimum time between any alien shots
    last_alien_move = 0
    alien_move_delay = 50  # milliseconds between alien movements
    last_alien_drop = 0
    alien_drop_cooldown = 300  # milliseconds between drops
    
    # Game loop
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if not game_over and not win:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        bullet = player.shoot()
                        if bullet:
                            player_bullets.add(bullet)
        
        if not game_over and not win:
            # Update player
            keys = pygame.key.get_pressed()
            player.update(keys)
            
            # Update bullets and clean up off-screen bullets
            for bullet in list(player_bullets):
                if bullet.update():
                    # Bullet went off screen, remove from player's bullet list
                    if bullet in player.bullets:
                        player.bullets.remove(bullet)
            
            alien_bullets.update()
            
            # Handle alien movement with timing
            if current_time - last_alien_move > alien_move_delay:
                aliens_need_drop = False
                
                # Check if any alien hits screen edge
                for alien in aliens:
                    if alien.rect.left <= 0 or alien.rect.right >= SCREEN_WIDTH:
                        aliens_need_drop = True
                        break
                
                # Move all aliens
                for alien in aliens:
                    alien.update(current_time, alien_speed)
                
                # Handle alien swarm drop and direction change
                if aliens_need_drop and current_time - last_alien_drop > alien_drop_cooldown:
                    # Change direction for all aliens and drop them down
                    for alien in aliens:
                        alien.direction *= -1
                        alien.rect.y += ALIEN_DROP
                    # Increase alien speed by 0.5 when they drop
                    alien_speed += 0.5
                    last_alien_drop = current_time
                
                last_alien_move = current_time
            
            # Handle alien shooting with global cooldown
            if current_time - last_alien_shot > global_alien_shot_cooldown:
                # Find bottom aliens in each column that want to shoot
                shooting_aliens = []
                for alien in aliens:
                    if alien.should_shoot(current_time):
                        # Only bottom aliens in each column can shoot
                        column_aliens = [a for a in aliens if a.rect.x == alien.rect.x]
                        if alien == max(column_aliens, key=lambda a: a.rect.y):
                            shooting_aliens.append(alien)
                
                # Let one random alien shoot
                if shooting_aliens:
                    shooting_alien = random.choice(shooting_aliens)
                    bullet = Bullet(shooting_alien.rect.centerx, shooting_alien.rect.bottom, 1)
                    alien_bullets.add(bullet)
                    last_alien_shot = current_time
            
            # Check collisions
            player_hit, score = check_collisions(player, player_bullets, alien_bullets, aliens, score)
            if player_hit:
                lives -= 1
                if lives <= 0:
                    game_over = True
                else:
                    # Reset player position and pause briefly
                    player.rect.x = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
                    pygame.time.wait(1000)
            
            # Check if aliens reached the bottom
            for alien in aliens:
                if alien.rect.bottom >= player.rect.top:
                    game_over = True
                    break
            
            # Check if all aliens are destroyed (win condition)
            if len(aliens) == 0:
                win = True
            
            # Speed up aliens as they are destroyed
            alien_speed = ALIEN_SPEED + (ALIEN_ROWS * ALIEN_COLS - len(aliens)) // 10
        
        # Draw everything
        screen.fill(BLACK)
        
        # Draw game objects
        screen.blit(player.image, player.rect)
        aliens.draw(screen)
        player_bullets.draw(screen)
        alien_bullets.draw(screen)
        
        # Draw UI
        draw_ui(screen, score, lives, font)
        
        # Draw game over or win message
        if game_over:
            draw_game_over(screen, "GAME OVER", font)
        elif win:
            draw_game_over(screen, "YOU WIN!", font)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
