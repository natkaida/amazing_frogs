import pygame
import random

pygame.init()
WIDTH, HEIGHT = 450, 600 
CELL_SIZE = 50  
GRID_WIDTH = 6  
GRID_HEIGHT = 12  
COLORS = [(0, 0, 225), (0, 225, 0), (225, 0, 0), (225, 225, 0)]
LIGHT_COLORS = [(30, 30, 255), (50, 255, 50), (255, 30, 30), (255, 255, 30)]
png_image = pygame.image.load('frog.png')
png_image = pygame.transform.smoothscale(png_image, (20, 20))
png_image.set_alpha(128)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Amazing Frogs")

class Block:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.stopped = False  
    
    def fall(self):
        if not self.stopped:
            self.y += 1
    
    def move_left(self, grid):
        if not self.stopped and self.x > 0 and not grid[self.y][self.x - 1]:
            self.x -= 1
    
    def move_right(self, grid):
        if not self.stopped and self.x < GRID_WIDTH - 1 and not grid[self.y][self.x + 1]:
            self.x += 1

    def draw(self, screen):
        color_index = COLORS.index(self.color)
        light_color = LIGHT_COLORS[color_index]      
        pygame.draw.rect(screen, self.color, (self.x * CELL_SIZE + 1, self.y * CELL_SIZE + 1, CELL_SIZE - 1, CELL_SIZE - 1), 0, 3)     
        pygame.draw.rect(screen, light_color, (self.x * CELL_SIZE + 3, self.y * CELL_SIZE + 3, CELL_SIZE - 6, CELL_SIZE - 6), 0, 3)       
        png_pos = (self.x * CELL_SIZE + (CELL_SIZE // 2 - 10), self.y * CELL_SIZE + (CELL_SIZE // 2 - 10))  
        screen.blit(png_image, png_pos)

class Trimino:
    def __init__(self):
        self.blocks = [
            Block(GRID_WIDTH // 2 - 1, 0, random.choice(COLORS)),
            Block(GRID_WIDTH // 2, 0, random.choice(COLORS)),
            Block(GRID_WIDTH // 2 + 1, 0, random.choice(COLORS)),
        ]
    
    def rotate_colors(self):        
        colors = [block.color for block in self.blocks]
        colors = [colors[-1]] + colors[:-1]
        for i in range(3):
            self.blocks[i].color = colors[i]
    
    def fall(self):
        for block in self.blocks:
            block.fall()

    def move_left(self, grid):
        if all(block.x > 0 and not grid[block.y][block.x - 1] for block in self.blocks):
            for block in self.blocks:
                block.move_left(grid)

    def move_right(self, grid):
        if all(block.x < GRID_WIDTH - 1 and not grid[block.y][block.x + 1] for block in self.blocks):
            for block in self.blocks:
                block.move_right(grid)

    def drop_down(self, grid):        
        while all(not block.stopped and not self.check_collision(block, grid) for block in self.blocks):
            self.fall()

    def check_collision(self, block, grid):
        if block.y >= GRID_HEIGHT - 1:
            return True
        if grid[block.y + 1][block.x]:
            return True
        return False

    def draw(self, screen):
        for block in self.blocks:
            block.draw(screen)

class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font('MOSCOW2024.otf', 16)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Game:
    def __init__(self):
        self.reset_game()
        self.font = pygame.font.Font('MOSCOW2024.otf', 15)  
        self.font_color = (255, 255, 255)
        self.restart_button = Button(WIDTH // 2 - 105, HEIGHT // 2 + 50, 130, 40, "Новая игра", (0, 255, 0), (0, 0, 0))
        self.exit_button = Button(WIDTH // 2 + 45, HEIGHT // 2 + 50, 80, 40, "Выйти", (255, 0, 0), (255, 255, 255))

    def reset_game(self):
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_trimino = Trimino()
        self.next_trimino = Trimino()  
        self.game_over = False
        self.fall_time = 0
        self.fall_speed = 500
        self.score = 0
        self.level = 1
        self.blocks_burned = 0

    def check_collision(self, block):
        if block.y >= GRID_HEIGHT - 1:
            return True
        if self.grid[block.y + 1][block.x]:
            return True
        return False

    def lock_trimino(self):
        for block in self.current_trimino.blocks:
            self.grid[block.y][block.x] = block.color
        self.check_lines()

        if any(self.grid[0][x] is not None for x in range(GRID_WIDTH)):
            self.game_over = True
        else:
            self.current_trimino = self.next_trimino
            self.next_trimino = Trimino()  

    def draw_next_trimino(self, screen):
        next_area_x = WIDTH - 140
        next_area_y = 280

        for i, block in enumerate(self.next_trimino.blocks):
            original_x, original_y = block.x, block.y
            block.x = (next_area_x // CELL_SIZE) + i 
            block.y = next_area_y // CELL_SIZE + 1    
            block.draw(screen) 
            block.x, block.y = original_x, original_y

    def find_matches(self):
        to_remove = set()

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH - 2):
                if self.grid[y][x] and self.grid[y][x] == self.grid[y][x + 1] == self.grid[y][x + 2]:
                    to_remove.update([(y, x), (y, x + 1), (y, x + 2)])

        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT - 2):
                if self.grid[y][x] and self.grid[y][x] == self.grid[y + 1][x] == self.grid[y + 2][x]:
                    to_remove.update([(y, x), (y + 1, x), (y + 2, x)])

        for y in range(GRID_HEIGHT - 2):
            for x in range(GRID_WIDTH - 2):
                if self.grid[y][x] and self.grid[y][x] == self.grid[y + 1][x + 1] == self.grid[y + 2][x + 2]:
                    to_remove.update([(y, x), (y + 1, x + 1), (y + 2, x + 2)])
                if self.grid[y][x + 2] and self.grid[y][x + 2] == self.grid[y + 1][x + 1] == self.grid[y + 2][x]:
                    to_remove.update([(y, x + 2), (y + 1, x + 1), (y + 2, x)])

        return to_remove

    def remove_matches(self, to_remove):
        for x in range(GRID_WIDTH):
            col_blocks = [(y, x) for y, cx in to_remove if cx == x]
            col_blocks.sort(reverse=True)  

            for y, _ in col_blocks:
                for row in range(y, 0, -1):
                    self.grid[row][x] = self.grid[row - 1][x]
                self.grid[0][x] = None  

        burned_blocks = len(to_remove)
        self.blocks_burned += burned_blocks
        self.score += burned_blocks
        if self.blocks_burned >= 20:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.blocks_burned = 0
        self.fall_speed = max(100, self.fall_speed - 50)  

    def check_lines(self):
        to_remove = self.find_matches()
        while to_remove:
            self.remove_matches(to_remove)
            to_remove = self.find_matches()  

    def update(self):
        if self.game_over:
            return  
        
        current_time = pygame.time.get_ticks()
        if current_time - self.fall_time > self.fall_speed:
            self.fall_time = current_time
            for block in self.current_trimino.blocks:
                if not block.stopped and self.check_collision(block):
                    block.stopped = True

            if all(block.stopped for block in self.current_trimino.blocks):
                self.lock_trimino()  
                self.check_lines()  
            else:
                self.current_trimino.fall()

    def draw(self, screen):
        if not self.game_over:
            self.current_trimino.draw(screen)

            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    if self.grid[y][x]:
                        block = Block(x, y, self.grid[y][x])
                        block.draw(screen)

            stats_background_color = (50, 50, 50)  
            stats_rect = pygame.Rect(WIDTH - 150, 0, 150, HEIGHT)  
            pygame.draw.rect(screen, stats_background_color, stats_rect)  
            score_text = self.font.render(f"Счет: {self.score}", True, self.font_color)
            level_text = self.font.render(f"Уровень: {self.level}", True, self.font_color)
            next_text = self.font.render("Следующая:", True, self.font_color)
            pause_text = self.font.render("Пауза: пробел", True, self.font_color)
            esc_text = self.font.render("Выход: Esc", True, self.font_color)
            screen.blit(score_text, (WIDTH - 140, 20))
            screen.blit(level_text, (WIDTH - 140, 60))
            screen.blit(next_text, (WIDTH - 140, 250))
            screen.blit(pause_text, (WIDTH - 140, 400))
            screen.blit(esc_text, (WIDTH - 140, 450))
            self.draw_next_trimino(screen)
        else:
            screen.fill((0, 0, 0))
            text = self.font.render("Игра закончена", True, (255, 0, 0))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text, text_rect)
            self.restart_button.draw(screen)
            self.exit_button.draw(screen)     

game = Game()
clock = pygame.time.Clock()
running = True
paused = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE and not game.game_over:
                paused = not paused
            elif not paused and not game.game_over:
                if event.key == pygame.K_LEFT:
                    game.current_trimino.move_left(game.grid)
                elif event.key == pygame.K_RIGHT:
                    game.current_trimino.move_right(game.grid)
                elif event.key == pygame.K_UP:
                    game.current_trimino.rotate_colors()
                elif event.key == pygame.K_DOWN:
                    game.current_trimino.drop_down(game.grid)
        elif event.type == pygame.MOUSEBUTTONDOWN and game.game_over:
            if game.restart_button.is_clicked(event.pos):
                game.reset_game()
            elif game.exit_button.is_clicked(event.pos):
                running = False

    screen.fill((0, 0, 0))
    if not paused and not game.game_over:
        game.update()
    game.draw(screen)
    if paused:
        font = pygame.font.Font('MOSCOW2024.otf', 20)
        text = font.render("Нажмите пробел для продолжения", True, (255, 255, 255))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
