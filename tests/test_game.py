"""Pruebas sin ventana visible: ejecutar con unittest discover -s tests -v."""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

from collections import defaultdict
import unittest
import pygame
from main import Bullet, Game, HEIGHT, MAX_LEVEL, WIDTH


class GameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.game = Game()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        pygame.event.clear()
        self.game.reset()
        self.keys = defaultdict(bool)

    def test_movement_is_limited_and_time_based(self):
        player = self.game.player
        start = player.x
        player.move(1, 0.1)
        self.assertAlmostEqual(player.x - start, player.speed * 0.1)
        player.move(1, 100)
        self.assertLessEqual(player.rect.right, WIDTH - 16)
        player.move(-1, 100)
        self.assertGreaterEqual(player.rect.left, 16)

    def test_shot_cooldown_and_offscreen_cleanup(self):
        self.game.shoot()
        self.game.shoot()
        self.assertEqual(len(self.game.bullets), 1)
        self.game.update(0.25, self.keys)
        self.game.shoot()
        self.assertEqual(len(self.game.bullets), 2)
        self.game.bullets.update(10)
        self.assertEqual(len(self.game.bullets), 0)
        bullet = Bullet((100, HEIGHT - 1), 200, self.game.enemy_bullet_image)
        self.game.enemy_bullets.add(bullet)
        self.game.enemy_bullets.update(1)
        self.assertEqual(len(self.game.enemy_bullets), 0)

    def test_enemy_hit_gives_points_and_removes_bullet(self):
        enemy = next(iter(self.game.enemies))
        self.game.bullets.add(Bullet(enemy.rect.center, 0, self.game.bullet_image))
        self.game.update(0, self.keys)
        self.assertEqual(self.game.score, enemy.points)
        self.assertEqual(len(self.game.enemies), 39)
        self.assertEqual(len(self.game.bullets), 0)

    def hit_player(self):
        self.game.enemy_bullets.add(Bullet(self.game.player.rect.center, 0, self.game.enemy_bullet_image))
        self.game.update(0, self.keys)

    def test_lives_invulnerability_and_game_over(self):
        self.game.invulnerable = 0
        self.hit_player()
        self.assertEqual(self.game.lives, 2)
        self.hit_player()
        self.assertEqual(self.game.lives, 2)
        for _ in range(2):
            self.game.invulnerable = 0
            self.hit_player()
        self.assertEqual(self.game.lives, 0)
        self.assertEqual(self.game.state, "game_over")

    def test_progression_and_victory(self):
        for level in range(1, MAX_LEVEL + 1):
            self.assertEqual(self.game.level, level)
            self.game.enemies.empty()
            self.game.update(0, self.keys)
        self.assertEqual(self.game.state, "victory")

    def test_enemy_reaching_player_ends_game(self):
        enemy = next(iter(self.game.enemies))
        enemy.move(0, self.game.player.rect.top - enemy.rect.bottom)
        self.game.update(0, self.keys)
        self.assertEqual(self.game.state, "game_over")

    def test_pause_freezes_simulation_and_resumes(self):
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p))
        self.game.escape()
        self.assertEqual(self.game.state, "paused")
        self.keys[pygame.K_RIGHT] = True
        x = self.game.player.x
        self.game.update(1, self.keys)
        self.assertEqual(self.game.player.x, x)
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p))
        self.game.escape()
        self.assertEqual(self.game.state, "playing")

    def test_restart_resets_all_gameplay_values(self):
        self.game.score = 999
        self.game.lives = 0
        self.game.level = 5
        self.game.state = "game_over"
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))
        self.game.escape()
        self.assertEqual((self.game.score, self.game.lives, self.game.level), (0, 3, 1))
        self.assertEqual(len(self.game.enemies), 40)
        self.assertEqual(self.game.state, "playing")

    def test_close_is_processed_after_other_event(self):
        pygame.event.post(pygame.event.Event(pygame.MOUSEMOTION, pos=(0, 0)))
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        self.game.escape()
        self.assertFalse(self.game.running)
        self.game.running = True

    def test_all_states_render(self):
        for state in ("menu", "playing", "paused", "game_over", "victory"):
            self.game.state = state
            self.game.draw()


if __name__ == "__main__":
    unittest.main()
