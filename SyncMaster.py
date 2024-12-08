import pygame
import sys
import random

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)

# Load images
BACKGROUND_IMAGE = 'Background1.jpeg'
PERFECT_IMAGE = pygame.transform.scale(pygame.image.load('Perfect.png'), (100, 100))
GOOD_IMAGE = pygame.transform.scale(pygame.image.load('Good.png'), (100, 100))
MISS_IMAGE = pygame.transform.scale(pygame.image.load('Miss.png'), (100, 100))

# Load audio file
AUDIO_FILE = 'Level1Song.wav'

# Load ArrowNote image and rotate for different directions
ARROW_NOTE_IMAGE = pygame.image.load('ArrowNote.png')
ARROW_NOTE_IMAGES = {
    'left': pygame.transform.rotate(pygame.transform.scale(ARROW_NOTE_IMAGE, (75, 75)), 180),
    'up': pygame.transform.rotate(pygame.transform.scale(ARROW_NOTE_IMAGE, (75, 75)), 90),
    'down': pygame.transform.rotate(pygame.transform.scale(ARROW_NOTE_IMAGE, (75, 75)), 270),
    'right': pygame.transform.scale(ARROW_NOTE_IMAGE, (75, 75))
}

# Renderer class
class Renderer:
    def __init__(self, screen):
        self.screen = screen

    def draw_background(self):
        background = pygame.transform.scale(pygame.image.load(BACKGROUND_IMAGE), (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(background, (0, 0))

    def display_result_image(self, image):
        self.screen.blit(image, (20, 20))  # Display in top left corner

# Note class
class Note:
    def __init__(self, direction):
        self.direction = direction
        self.image = ARROW_NOTE_IMAGES[direction]
        self.x, self.y = self.get_start_position()
        self.speed = 3  # Pixels per frame

    def get_start_position(self):
        if self.direction == 'left':
            return (SCREEN_WIDTH * 0.07, 0)
        elif self.direction == 'up':
            return (SCREEN_WIDTH * 0.32, 0)
        elif self.direction == 'down':
            return (SCREEN_WIDTH * 0.59, 0)
        elif self.direction == 'right':
            return (SCREEN_WIDTH * 0.83, 0)

    def update_position(self):
        self.y += self.speed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

# InputHandler class
class InputHandler:
    def __init__(self):
        self.key_mapping = {
            pygame.K_LEFT: 'left',
            pygame.K_UP: 'up',
            pygame.K_DOWN: 'down',
            pygame.K_RIGHT: 'right'
        }

    def get_key_pressed(self, event):
        if event.key in self.key_mapping:
            return self.key_mapping[event.key]
        return None

# ScoringSystem class
class ScoringSystem:
    def __init__(self):
        self.score = 0
        self.current_combo = 0
        self.best_combo = 0
        self.stats = {"perfect": 0, "early": 0, "late": 0}

    def check_hit(self, note, key_pressed):
        hit_points = {
            'left': (SCREEN_WIDTH * 0.07, SCREEN_HEIGHT * 0.86),
            'up': (SCREEN_WIDTH * 0.32, SCREEN_HEIGHT * 0.86),
            'down': (SCREEN_WIDTH * 0.59, SCREEN_HEIGHT * 0.86),
            'right': (SCREEN_WIDTH * 0.83, SCREEN_HEIGHT * 0.86)
        }
        hit_x, hit_y = hit_points[note.direction]
        y_distance = note.y - hit_y  # Positive means late, negative means early

        # Relaxed margins
        perfect_margin = 20
        good_margin = 35

        if abs(y_distance) <= perfect_margin and key_pressed == note.direction:
            self.score += 100
            self.current_combo += 1
            if self.current_combo > self.best_combo:
                self.best_combo = self.current_combo
            self.stats["perfect"] += 1
            return "perfect", 100, ""  # No early/late for perfect
        elif abs(y_distance) <= good_margin and key_pressed == note.direction:
            self.score += 50
            self.current_combo = 0  # Reset combo on good
            self.stats["early" if y_distance > 0 else "late"] += 1
            return "good", 50, " (slightly early)" if y_distance < 0 else " (slightly late)"  # Fixed: early when y_distance < 0
        else:
            self.current_combo = 0  # Reset combo on miss
            self.stats["early" if y_distance > 0 else "late"] += 1
            return "miss", 0, " (late)" if y_distance > 0 else " (early)"

# AudioManager class
class AudioManager:
    def __init__(self):
        pygame.mixer.music.load(AUDIO_FILE)

    def play_music(self):
        pygame.mixer.music.play(-1)  # Loop the music

    def stop_music(self):
        pygame.mixer.music.stop()

# Game class
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Rhythm Game")
        self.renderer = Renderer(self.screen)
        self.input_handler = InputHandler()
        self.audio_manager = AudioManager()
        self.scoring_system = ScoringSystem()
        self.arrow_notes = []
        self.last_arrow_time = pygame.time.get_ticks()
        self.running = True
        self.start_time = pygame.time.get_ticks() + 3000  # Start 3 seconds after the game begins
        self.end_time = self.start_time + 30000  # Stop 30 seconds after notes start

    def run(self):
        self.audio_manager.play_music()
        while self.running:
            current_time = pygame.time.get_ticks()
            self.handle_events()
            self.update_notes(current_time)
            self.draw()
            pygame.display.flip()
            clock.tick(60)
        self.audio_manager.stop_music()
        self.display_results()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                key_pressed = self.input_handler.get_key_pressed(event)
                if key_pressed:
                    for note in self.arrow_notes:
                        result, points, early_late = self.scoring_system.check_hit(note, key_pressed)
                        combo_bonus = 200 if self.scoring_system.current_combo > 1 else 0  # Combo bonus for 2+ perfects
                        if combo_bonus:
                            print(f"Hit result: {result}{early_late}, Points: {points} +{combo_bonus} (Combo Streak: {self.scoring_system.current_combo})")
                        else:
                            print(f"Hit result: {result}{early_late}, Points: {points}")
                        self.arrow_notes.remove(note)
                        break  # Only check the first hit

    def update_notes(self, current_time):
        if self.start_time <= current_time <= self.end_time:
            if current_time - self.last_arrow_time > 1500:
                direction = random.choice(['left', 'up', 'down', 'right'])
                new_arrow = Note(direction)
                self.arrow_notes.append(new_arrow)
                self.last_arrow_time = current_time

        for note in self.arrow_notes:
            note.update_position()
            if note.y > SCREEN_HEIGHT:
                self.arrow_notes.remove(note)

    def draw(self):
        self.renderer.draw_background()
        for note in self.arrow_notes:
            note.draw(self.screen)

    def display_results(self):
        print("Thanks for playing!")
        print(f"Total Score: {self.scoring_system.score}")
        print(f"Best Combo Streak: {self.scoring_system.best_combo}")
        stats = self.scoring_system.stats
        if stats["perfect"] == sum(stats.values()):
            print("You got rhythm!")
        elif stats["early"] > stats["late"]:
            print("You have a tendency towards late inputs.")
        elif stats["late"] > stats["early"]:
            print("You have a tendency towards early inputs.")
        else:
            print("Your inputs are equally early and late!")

if __name__ == "__main__":
    clock = pygame.time.Clock()
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()
