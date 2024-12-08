import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Initialize the audio system
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)

# Load background image
BACKGROUND_IMAGE = 'Background1.jpeg'

# Load result images
PERFECT_IMAGE = pygame.image.load('Perfect.png')
GOOD_IMAGE = pygame.image.load('Good.png')
MISS_IMAGE = pygame.image.load('Miss.png')

# Scale the images
PERFECT_IMAGE = pygame.transform.scale(PERFECT_IMAGE, (100, 100))  # Adjust size as needed
GOOD_IMAGE = pygame.transform.scale(GOOD_IMAGE, (100, 100))
MISS_IMAGE = pygame.transform.scale(MISS_IMAGE, (100, 100))

# Function to display result images on the screen
def display_result_image(image):
    screen.blit(image, (20, 20))  # Display in top left corner

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

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rhythm Game")

# Load and scale the background image
background = pygame.image.load(BACKGROUND_IMAGE)
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Clock for controlling frame rate
clock = pygame.time.Clock()

# ArrowNote class
class ArrowNote:
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

# Function to check if a key press is correct
def check_hit(arrow_note, key_pressed):
    hit_points = {
        'left': (SCREEN_WIDTH * 0.07, SCREEN_HEIGHT * 0.87), 
        'up': (SCREEN_WIDTH * 0.32, SCREEN_HEIGHT * 0.87),
        'down': (SCREEN_WIDTH * 0.59, SCREEN_HEIGHT * 0.87),
        'right': (SCREEN_WIDTH * 0.83, SCREEN_HEIGHT * 0.87)
    }
    hit_x, hit_y = hit_points[arrow_note.direction]

    # Calculate distances
    x_distance = abs(arrow_note.x - hit_x)
    y_distance = abs(arrow_note.y - hit_y)

    # Check for "perfect"
    if x_distance < 15 and y_distance < 15:
        if key_pressed == arrow_note.direction:
            display_result_image(PERFECT_IMAGE)
            print("Hit result: perfect")
            return "perfect"
    
    # Check for "good" (either early or late)
    elif 15 <= x_distance <= 27 or 15 <= y_distance <= 27:
        if key_pressed == arrow_note.direction:
            display_result_image(GOOD_IMAGE)
            print("Hit result: good")
            return "good"

    # Anything else is a "miss"
    display_result_image(MISS_IMAGE)
    print("Hit result: miss")
    return "miss"

# Main game loop
def game_loop():
    # Start playing the audio
    pygame.mixer.music.load(AUDIO_FILE)
    pygame.mixer.music.play(-1)  # The `-1` makes the song loop continuously

    running = True
    arrow_notes = []
    last_arrow_time = pygame.time.get_ticks()

    # Set the time for when notes start and stop falling
    start_time = pygame.time.get_ticks() + 3000  # Start 3 seconds after the game begins
    end_time = start_time + 30000  # Stop 30 seconds after notes start

    while running:
        current_time = pygame.time.get_ticks()

        # Check if the current time is within the time range for generating notes
        if start_time <= current_time <= end_time:
            # Generate a new ArrowNote every 1 second
            if current_time - last_arrow_time > 1000:
                direction = random.choice(['left', 'up', 'down', 'right'])
                new_arrow = ArrowNote(direction)
                arrow_notes.append(new_arrow)
                last_arrow_time = current_time

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                key_mapping = {
                    pygame.K_LEFT: 'left',
                    pygame.K_UP: 'up',
                    pygame.K_DOWN: 'down',
                    pygame.K_RIGHT: 'right'
                }
                if event.key in key_mapping:
                    key_pressed = key_mapping[event.key]
                    for note in arrow_notes:
                        if note.y > SCREEN_HEIGHT * 0.85:  # Only check for notes near the bottom
                            result = check_hit(note, key_pressed)
                            print(f"Hit result: {result}")  # You can replace this with scoring logic

        # Update arrow notes
        for note in arrow_notes:
            note.update_position()
            if note.y > SCREEN_HEIGHT:
                arrow_notes.remove(note)

        # Draw everything
        screen.blit(background, (0, 0))
        for note in arrow_notes:
            note.draw(screen)
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

    # Stop the audio when the game ends
    pygame.mixer.music.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_loop()
