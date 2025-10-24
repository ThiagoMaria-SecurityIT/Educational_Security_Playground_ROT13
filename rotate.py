import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 150, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
RED = (255, 0, 0)
DARK_RED = (150, 0, 0)

# Font settings
FONT_SIZE = 36
SMALL_FONT_SIZE = 24
font = pygame.font.SysFont('Arial', FONT_SIZE)
small_font = pygame.font.SysFont('Arial', SMALL_FONT_SIZE)

class Button:
    def __init__(self, x, y, width, height, text, color, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hover_color = tuple(min(255, c + 30) for c in color)
        self.is_hovered = False
        
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class SlotMachineLetter:
    def __init__(self, x, y, original_char, target_char):
        self.x = x
        self.y = y
        self.original_char = original_char.upper()
        self.target_char = target_char.upper()
        self.current_char = original_char.upper()
        self.is_spinning = False
        self.spin_speed = 0
        self.spin_offset = 0
        self.alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.current_index = 0
        self.target_index = self.alphabet.index(self.target_char) if target_char.isalpha() else 0
        self.stopped = False
        self.has_started = False  # Track if spinning has started
        
    def start_spin(self):
        # Always start spinning for alphabetic characters
        if self.original_char.isalpha():
            self.is_spinning = True
            self.has_started = True
            self.spin_speed = 20
            self.spin_offset = 0
            self.current_index = self.alphabet.index(self.original_char)
            self.stopped = False
        else:
            # For non-alphabetic, mark as stopped immediately
            self.stopped = True
            self.has_started = True
            
    def update(self):
        if self.is_spinning and self.has_started:
            # Gradually slow down
            if self.spin_speed > 0:
                self.spin_offset += self.spin_speed
                if self.spin_offset >= 40:  # Move to next letter every 40 pixels
                    self.spin_offset = 0
                    self.current_index = (self.current_index + 1) % 26
                    self.current_char = self.alphabet[self.current_index]
                
                # Slow down gradually
                if self.spin_speed > 2:
                    self.spin_speed *= 0.98
                else:
                    # Check if we've reached the target
                    if self.current_char == self.target_char:
                        self.is_spinning = False
                        self.stopped = True
                        self.current_char = self.target_char
            else:
                self.is_spinning = False
                self.stopped = True
                self.current_char = self.target_char
                
    def draw(self, screen):
        if self.original_char.isalpha():
            if self.is_spinning and self.has_started:
                # Draw multiple rows for slot machine effect
                for i in range(-2, 3):
                    char_index = (self.current_index - i) % 26
                    char = self.alphabet[char_index]
                    
                    # Calculate alpha based on distance from center
                    alpha = 255 - abs(i) * 80
                    if alpha > 0:
                        # Create surface with alpha
                        text_surface = font.render(char, True, GREEN)
                        text_surface.set_alpha(alpha)
                        
                        # Calculate y position
                        y_pos = self.y + i * 40 - self.spin_offset
                        
                        # Only draw if within reasonable bounds
                        if -50 < y_pos < WINDOW_HEIGHT + 50:
                            screen.blit(text_surface, (self.x, y_pos))
            else:
                # Draw the final character
                color = GREEN if self.stopped else WHITE
                text_surface = font.render(self.current_char, True, color)
                screen.blit(text_surface, (self.x, self.y))
        else:
            # Draw non-alphabetic characters normally
            text_surface = font.render(self.original_char, True, WHITE)
            screen.blit(text_surface, (self.x, self.y))

class Rot13App:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("ROT13 is an obfuscation technique not a true encryption")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize pygame.scrap
        pygame.scrap.init()
        
        # Input field
        self.input_rect = pygame.Rect(50, 50, WINDOW_WIDTH - 100, 50)
        self.input_text = ""
        self.input_active = False
        
        # Buttons
        self.encrypt_button = Button(200, 500, 150, 50, "Encrypt", DARK_GREEN)
        self.decrypt_button = Button(450, 500, 150, 50, "Decrypt", DARK_RED)
        
        # Slot machine letters
        self.slot_letters = []
        
        # Animation state
        self.is_animating = False
        self.animation_complete = False
        self.animation_start_time = 0
        
        # Track which operation was performed
        self.last_operation = None  # Will be "encrypt" or "decrypt"
        
    def rot13(self, text):
        """Correct ROT13 implementation"""
        result = ""
        for char in text:
            if 'A' <= char <= 'Z':
                # Shift uppercase letters by 13
                result += chr((ord(char) - ord('A') + 13) % 26 + ord('A'))
            elif 'a' <= char <= 'z':
                # Shift lowercase letters by 13
                result += chr((ord(char) - ord('a') + 13) % 26 + ord('a'))
            else:
                # Keep non-alphabetic characters unchanged
                result += char
        return result
    
    def start_animation(self, encrypt=True):
        if not self.input_text:
            return
            
        self.is_animating = True
        self.animation_complete = False
        self.animation_start_time = pygame.time.get_ticks()
        
        # Track which operation was performed
        self.last_operation = "encrypt" if encrypt else "decrypt"
        
        # Calculate target text using ROT13
        target_text = self.rot13(self.input_text)
        
        # Create slot machine letter objects
        self.slot_letters = []
        x_start = 50
        y_pos = 250
        
        for i, char in enumerate(self.input_text):
            original_char = char
            target_char = target_text[i]
            
            # Create slot machine letter for each character
            slot_letter = SlotMachineLetter(
                x_start + i * 45, 
                y_pos, 
                original_char, 
                target_char
            )
            self.slot_letters.append(slot_letter)
        
        # Start all spinning immediately with manual stagger
        self.stagger_start_time = pygame.time.get_ticks()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            # Handle input field
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.input_active = self.input_rect.collidepoint(event.pos)
                
            if event.type == pygame.KEYDOWN:
                if self.input_active:
                    # Handle copy (Ctrl+C)
                    if event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        if self.input_text:  # Only copy if there's text
                            pygame.scrap.put(pygame.SCRAP_TEXT, self.input_text.encode('utf-8'))
                    
                    # Handle paste (Ctrl+V)
                    elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        try:
                            # Check if clipboard has text
                            if pygame.scrap.get_types():
                                pasted_data = pygame.scrap.get(pygame.SCRAP_TEXT)
                                if pasted_data:
                                    pasted_text = pasted_data.decode('utf-8')
                                    # Filter out any null characters or invalid characters
                                    pasted_text = ''.join(c for c in pasted_text if c.isprintable())
                                    self.input_text += pasted_text
                        except Exception as e:
                            print(f"Clipboard error: {e}")
                            pass  # Ignore clipboard errors
                    
                    # Handle backspace
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    
                    # Handle regular input
                    elif event.unicode.isalnum() or event.unicode.isspace():
                        self.input_text += event.unicode
            
            # Handle buttons
            if self.encrypt_button.handle_event(event):
                self.start_animation(encrypt=True)
                
            if self.decrypt_button.handle_event(event):
                self.start_animation(encrypt=False)  # ROT13 is symmetric
    
    def update(self):
        # Handle staggered start manually
        if self.is_animating and self.slot_letters:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.stagger_start_time
            
            for i, letter in enumerate(self.slot_letters):
                # Start each letter after a delay
                if elapsed > i * 150 and not letter.has_started:
                    letter.start_spin()
        
        # Update slot machine letters
        all_stopped = True
        for letter in self.slot_letters:
            letter.update()
            if not letter.stopped:
                all_stopped = False
        
        if self.is_animating and all_stopped and self.slot_letters:
            # Check if all letters have at least started
            all_started = all(letter.has_started for letter in self.slot_letters)
            if all_started:
                self.is_animating = False
                self.animation_complete = True
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw title
        title_text = font.render("ROT13 Encryption Animation", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 20))
        self.screen.blit(title_text, title_rect)
        
        # Draw input field
        pygame.draw.rect(self.screen, WHITE if self.input_active else GRAY, self.input_rect, 2)
        
        # Ensure input_text is valid before rendering
        try:
            input_surface = font.render(self.input_text, True, WHITE)
            self.screen.blit(input_surface, (self.input_rect.x + 5, self.input_rect.y + 5))
        except ValueError:
            # If there's an issue with the text, reset it
            self.input_text = ""
            input_surface = font.render("", True, WHITE)
            self.screen.blit(input_surface, (self.input_rect.x + 5, self.input_rect.y + 5))
        
        # Draw input label
        input_label = small_font.render("Input Text:", True, WHITE)
        self.screen.blit(input_label, (self.input_rect.x, self.input_rect.y - 25))
        
        # Draw output label
        if self.slot_letters:
            output_label = small_font.render("Output Text:", True, WHITE)
            self.screen.blit(output_label, (50, 220))
        
        # Draw slot machine letters
        for letter in self.slot_letters:
            letter.draw(self.screen)
        
        # Draw buttons
        self.encrypt_button.draw(self.screen)
        self.decrypt_button.draw(self.screen)
        
        # Draw completion message based on last operation
        if self.animation_complete:
            if self.last_operation == "encrypt":
                complete_text = small_font.render("Encrypted!", True, GREEN)
            else:
                complete_text = small_font.render("Decrypted!", True, GREEN)
            complete_rect = complete_text.get_rect(center=(WINDOW_WIDTH // 2, 450))
            self.screen.blit(complete_text, complete_rect)
        
        # Draw instructions
        if not self.slot_letters:
            instructions = small_font.render("Type text above and click Encrypt or Decrypt", True, GRAY)
            instructions_rect = instructions.get_rect(center=(WINDOW_WIDTH // 2, 350))
            self.screen.blit(instructions, instructions_rect)
        
        # Draw copy/paste hint
        copy_paste_hint = small_font.render("Use Ctrl+C to copy and Ctrl+V to paste", True, GRAY)
        copy_paste_rect = copy_paste_hint.get_rect(center=(WINDOW_WIDTH // 2, 380))
        self.screen.blit(copy_paste_hint, copy_paste_rect)
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# Run the application
if __name__ == "__main__":
    app = Rot13App()
    app.run()
