import pygame

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)

# Load images
BACKGROUND_IMAGE = 'Background2.jpeg'
CIRCULAR_NOTE_IMAGE = pygame.image.load('Circular.png')
COUNTDOWN_IMAGES = {
    3: pygame.image.load('threetransp.png'),
    2: pygame.image.load('twotransp.png'),
    1: pygame.image.load('onetransp.png'),
    0: pygame.image.load('Now.png')
}

# Renderer class with Singleton pattern
class Renderer:
    _instance = None  # Class-level reference to the single instance

    def __new__(cls, screen):
        if cls._instance is None:
            # Create the instance and store it
            cls._instance = super(Renderer, cls).__new__(cls)
            cls._instance.screen = screen  # Initialize instance attribute
        return cls._instance

    def draw_background(self):
        background = pygame.transform.scale(pygame.image.load(BACKGROUND_IMAGE), (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(background, (0, 0))

    def draw_countdown(self, number):
        if number in COUNTDOWN_IMAGES:
            countdown_image = pygame.transform.scale(COUNTDOWN_IMAGES[number], (100, 100))
            self.screen.blit(countdown_image, (20, 85))

# Note class
class Note:
    def __init__(self):
        self.image = pygame.transform.scale(CIRCULAR_NOTE_IMAGE, (75, 75))
        self.x = SCREEN_WIDTH // 2 - 37  # Centered horizontally
        self.y = 0  # Start at the top
        self.target_y = SCREEN_HEIGHT // 2 + 100
        self.speed = (self.target_y - self.y) / 3000  # Pixels per ms

    def update_position(self, elapsed_time):
        self.y = min(self.target_y, self.y + self.speed * elapsed_time)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

# Game class
class TrainingGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Rhythm Training Game")
        self.renderer = Renderer(self.screen)
        self.running = True
        self.notes = []
        self.last_press_time = None
        self.input_offsets = []
        self.tendency = None  # Initialize tendency to None
        self.note_positions = [] # Keep track of note positions 

    def get_user_input(self, prompt):
        print(prompt)
        return input().strip().lower()

    def start_sequence(self):
        print("Welcome to Rhythm Training!")
        self.tendency = self.get_user_input("Do you have a tendency towards late or early hits? Respond with: late, early, neither:")
        proceed = self.get_user_input("I see! Do you wish to begin the training sequence? Respond with: yes, no:")

        if proceed != 'yes':
            print("See you next time!")
            self.running = False
        else:
            # Store the tendency
            self.tendency = self.tendency
            pygame.time.delay(6000)

    def run(self):
        self.start_sequence()
        if not self.running:
            return

        clock = pygame.time.Clock()
        start_time = pygame.time.get_ticks()
        countdown_time = start_time + 3000
        end_time = start_time + 43000

        while self.running:
            current_time = pygame.time.get_ticks()
            self.handle_events(current_time)

            # Draw background
            self.renderer.draw_background()

            # Draw countdown (changed this)
            countdown_number = max(0, (countdown_time - current_time) // 1000)
            self.renderer.draw_countdown(countdown_number)

            # Generate and update notes
            if len(self.notes) == 0: # Generate a new note if there are no notes
                countdown_time = current_time + 3000 # Reset countdown timer
                self.notes.append(Note()) # Append a new note

            for note in self.notes:
                note.update_position(clock.get_time())
                note.draw(self.screen)
                self.note_positions.append((note.x, note.y)) # Store note position

            pygame.display.flip()
            clock.tick(60)

            if current_time >= end_time:
                self.evaluate_performance()
                self.running = False

        pygame.quit()

    def handle_events(self, current_time):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.process_input(current_time) 

    def process_input(self, current_time):
        if self.notes:
            note = self.notes.pop(0)
        offset = current_time - (pygame.time.get_ticks() - 3000)
        self.input_offsets.append(offset)
        if 365 <= note.y <= 385:  # Perfect timing range
            timing = "perfect"
        elif 355 <= note.y <= 385:  # Good timing ranges (inclusive of 364 and 385)
            timing = "good"
        else:
            timing = "miss"  # Outside good or perfect ranges
        print(f"Timing: {timing}, Offset: {offset} ms, Note Position: ({note.x}, {note.y})")

    def evaluate_performance(self):
        late_count = sum(1 for pos in self.note_positions if pos[1] > 375)
        early_count = sum(1 for pos in self.note_positions if pos[1] < 375)

        total_inputs = len(self.note_positions)

        if total_inputs == 0:
            print("No inputs were recorded. Please try again!")
            return

        if self.tendency == "late":
            if early_count > late_count:
                print("You no longer have a late tendency!")
            else:
                print("You still have a tendency towards late hits! Try the training mode again!")
        elif self.tendency == "early":
            if late_count > early_count:
                print("You no longer have an early tendency!")
            else:
                print("You still have a tendency towards early hits! Try the training mode again!")
        elif self.tendency == "neither":
            if early_count == late_count:
                print("You have no tendency towards early or late hits. Keep practicing!")
            else:
                dominant_tendency = "late" if late_count > early_count else "early"
                print(f"You now seem to have a tendency towards {dominant_tendency} hits. Keep training!")


if __name__ == "__main__":
    game = TrainingGame()
    game.run()
