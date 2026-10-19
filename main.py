"""Space Invaders: juego completo basado en los recursos del repositorio original."""

from pathlib import Path
import random

import pygame

BASE_DIR = Path(__file__).resolve().parent
WIDTH, HEIGHT = 800, 600
FPS = 60
MAX_LEVEL = 5
WHITE = (235, 242, 255)
CYAN = (83, 226, 240)


def load_image(name, size):
    """Las rutas funcionan aunque se ejecute desde otra carpeta."""
    image = pygame.image.load(str(BASE_DIR / "img" / name)).convert_alpha()
    return pygame.transform.smoothscale(image, size)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, center, velocity, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=center)
        self.position = pygame.Vector2(self.rect.topleft)
        self.velocity = velocity

    def update(self, dt):
        self.position.y += self.velocity * dt
        self.rect.topleft = round(self.position.x), round(self.position.y)
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, image, x, y, points):
        super().__init__()
        self.image = image
        self.rect = image.get_rect(topleft=(x, y))
        self.position = pygame.Vector2(x, y)
        self.points = points

    def move(self, dx, dy=0):
        self.position += pygame.Vector2(dx, dy)
        self.rect.topleft = round(self.position.x), round(self.position.y)


class Player(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 24))
        self.x = float(self.rect.x)
        self.speed = 340

    def move(self, direction, dt):
        self.x += direction * self.speed * dt
        self.x = max(16, min(self.x, WIDTH - 16 - self.rect.width))
        self.rect.x = round(self.x)


class Game:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Space Invaders | Hybridge")
        pygame.display.set_icon(load_image("title_icon.png", (32, 32)))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
        self.title_font = pygame.font.Font(None, 64)
        self.background = load_image("background.png", (WIDTH, HEIGHT))
        # Una capa oscura mejora el contraste del HUD y los proyectiles.
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((3, 8, 24, 115))
        self.background.blit(shade, (0, 0))
        self.player_image = load_image("player_image.png", (48, 48))
        self.enemy_images = [
            load_image("enemy_purple_image.png", (40, 34)),
            load_image("enemy_blue_image.png", (40, 34)),
            load_image("enemy_green_image.png", (40, 34)),
        ]
        self.bullet_image = load_image("bullet_image.png", (8, 20))
        self.enemy_bullet_image = pygame.Surface((6, 16), pygame.SRCALPHA)
        pygame.draw.rect(self.enemy_bullet_image, (255, 110, 130), (0, 0, 6, 16), border_radius=3)
        self.sounds = {}
        if pygame.mixer.get_init():
            for name in ("shoot", "hit", "finish"):
                try:
                    self.sounds[name] = pygame.mixer.Sound(str(BASE_DIR / "sounds" / f"{name}.wav"))
                    self.sounds[name].set_volume(0.18)
                except (pygame.error, OSError):
                    pass  # El juego también funciona sin dispositivo de audio.
        self.muted = False
        self.running = True
        self.reset()
        self.state = "menu"

    def play_sound(self, name):
        if not self.muted and name in self.sounds:
            self.sounds[name].play()

    def reset(self):
        self.player = Player(self.player_image)
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.score = 0
        self.lives = 3
        self.level = 1
        self.shot_timer = 0.0
        self.invulnerable = 1.5
        self.state = "playing"
        self.spawn_wave()

    def spawn_wave(self):
        self.bullets.empty()
        self.enemy_bullets.empty()
        self.enemies.empty()
        self.direction = 1
        self.enemy_shot_timer = 1.1
        for row in range(4):
            for column in range(10):
                self.enemies.add(Enemy(
                    self.enemy_images[min(row, 2)],
                    90 + column * 64, 100 + row * 48, (4 - row) * 10
                ))

    def finish(self, state):
        self.state = state
        self.play_sound("finish")

    def escape(self):
        """Procesa toda la cola de eventos, sin ignorar solicitudes de cierre."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_m:
                    self.muted = not self.muted
                elif event.key == pygame.K_RETURN and self.state in ("menu", "game_over", "victory"):
                    self.reset()
                elif event.key == pygame.K_r and self.state in ("game_over", "victory"):
                    self.reset()
                elif event.key == pygame.K_p and self.state in ("playing", "paused"):
                    self.state = "paused" if self.state == "playing" else "playing"
            elif event.type == pygame.WINDOWFOCUSLOST and self.state == "playing":
                self.state = "paused"

    def shoot(self):
        if self.state == "playing" and self.shot_timer <= 0:
            self.bullets.add(Bullet(self.player.rect.midtop, -520, self.bullet_image))
            self.shot_timer = 0.24
            self.play_sound("shoot")

    def over(self):
        if self.lives <= 0:
            self.finish("game_over")

    def update(self, dt, keys=None):
        if self.state != "playing":
            return
        if keys is None:
            keys = pygame.key.get_pressed()
        direction = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.player.move(direction, dt)
        self.shot_timer = max(0, self.shot_timer - dt)
        self.invulnerable = max(0, self.invulnerable - dt)
        if keys[pygame.K_SPACE]:
            self.shoot()
        self.bullets.update(dt)
        self.enemy_bullets.update(dt)

        dx = self.direction * (36 + self.level * 12) * dt
        if self.enemies:
            left = min(e.rect.left for e in self.enemies)
            right = max(e.rect.right for e in self.enemies)
            if right + dx > WIDTH - 20 or left + dx < 20:
                self.direction *= -1
                dx = self.direction * abs(dx)
                for enemy in self.enemies:
                    enemy.move(0, 20)
            for enemy in self.enemies:
                enemy.move(dx)

        # Cada bala puede eliminar como máximo un enemigo.
        for bullet in list(self.bullets):
            enemy = pygame.sprite.spritecollideany(bullet, self.enemies)
            if enemy:
                bullet.kill()
                enemy.kill()
                self.score += enemy.points
                self.play_sound("hit")

        self.enemy_shot_timer -= dt
        if self.enemies and self.enemy_shot_timer <= 0:
            # Disparan las naves inferiores para no atravesar a sus compañeros.
            columns = {}
            for enemy in self.enemies:
                column = round((enemy.position.x - next(iter(self.enemies)).position.x) / 64)
                if column not in columns or enemy.rect.bottom > columns[column].rect.bottom:
                    columns[column] = enemy
            shooter = random.choice(list(columns.values()))
            self.enemy_bullets.add(Bullet(shooter.rect.midbottom, 190 + self.level * 25, self.enemy_bullet_image))
            self.enemy_shot_timer = max(0.28, 1.1 - self.level * 0.13)

        hits = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
        if hits and self.invulnerable <= 0:
            self.lives -= 1
            self.invulnerable = 1.5
            self.play_sound("hit")
            self.over()
        if self.state != "playing":
            return
        if any(e.rect.bottom >= self.player.rect.top for e in self.enemies):
            self.finish("game_over")
            return
        if not self.enemies:
            if self.level == MAX_LEVEL:
                self.finish("victory")
            else:
                self.level += 1
                self.invulnerable = 1.5
                self.spawn_wave()

    def draw_HUD(self):
        pygame.draw.rect(self.window, (8, 17, 35), (0, 0, WIDTH, 64))
        pygame.draw.line(self.window, (40, 105, 125), (0, 64), (WIDTH, 64))
        labels = [f"PUNTOS  {self.score:05d}", f"VIDAS  {self.lives}", f"NIVEL  {self.level}/{MAX_LEVEL}", f"BALAS  {len(self.bullets)}"]
        for x, label in zip((20, 265, 435, 640), labels):
            self.window.blit(self.font.render(label, True, CYAN), (x, 22))
        footer = f"Flechas / A D: mover   ESPACIO: disparar   P: pausa   M: audio {'OFF' if self.muted else 'ON'}"
        self.window.blit(self.small_font.render(footer, True, WHITE), (20, HEIGHT - 20))

    def draw_overlay(self, title, lines):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((3, 8, 22, 205))
        self.window.blit(overlay, (0, 0))
        pygame.draw.rect(self.window, (12, 27, 47), (80, 165, 640, 285), border_radius=16)
        pygame.draw.rect(self.window, (44, 139, 159), (80, 165, 640, 285), 2, border_radius=16)
        label = self.title_font.render(title, True, CYAN)
        self.window.blit(label, label.get_rect(center=(WIDTH // 2, 220)))
        for index, line in enumerate(lines):
            label = self.font.render(line, True, WHITE)
            self.window.blit(label, label.get_rect(center=(WIDTH // 2, 292 + index * 34)))

    def draw(self):
        self.window.blit(self.background, (0, 0))
        self.enemies.draw(self.window)
        self.bullets.draw(self.window)
        self.enemy_bullets.draw(self.window)
        if self.invulnerable <= 0 or int(self.invulnerable * 12) % 2 == 0:
            self.window.blit(self.player.image, self.player.rect)
        self.draw_HUD()
        if self.state == "menu":
            self.draw_overlay("SPACE INVADERS", ["Protege la Tierra durante 5 oleadas.", "Flechas / A D: mover | ESPACIO: disparar", "ENTER: comenzar | ESC: salir"])
        elif self.state == "paused":
            self.draw_overlay("PAUSA", ["Pulsa P para continuar", "M: activar o silenciar el audio", "ESC: salir"])
        elif self.state in ("game_over", "victory"):
            title = "VICTORIA" if self.state == "victory" else "GAME OVER"
            self.draw_overlay(title, [f"Puntuacion final: {self.score}", "ENTER / R: nueva partida", "ESC: salir"])
        pygame.display.flip()

    def run(self):
        try:
            while self.running:
                # Limita saltos tras arrastrar la ventana o recuperar el foco.
                dt = min(self.clock.tick(FPS) / 1000, 0.05)
                self.escape()
                if self.running:
                    self.update(dt)
                    self.draw()
        finally:
            pygame.quit()


if __name__ == "__main__":
    Game().run()
