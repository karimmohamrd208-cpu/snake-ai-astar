from heapq import heappop, heappush
from random import randint
import pygame
from pygame import KEYDOWN, K_SPACE, K_q, K_r, QUIT, display, draw, time


# ============================================================================
# SECTION 1: A* PATHFINDING ALGORITHM
# ============================================================================


class PriorityQueue:

  def __init__(self):
    self.elements = []
    self.counter = 0

  def empty(self):
    """Check if queue is empty"""
    return len(self.elements) == 0

  def put(self, item, priority):
    """Add item with given priority"""
    heappush(self.elements, (priority, self.counter, item))
    self.counter += 1

  def get(self):
    """Get item with lowest priority"""
    return heappop(self.elements)[2]


def manhattan_distance(pos1, pos2):
  return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def get_neighbors(position, snake_body, grid_width, grid_height):
  x, y = position
  neighbors = []

  # 4 directions: right, left, down, up
  directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

  for dx, dy in directions:
    new_x, new_y = x + dx, y + dy

    # Check if within grid bounds
    if 0 <= new_x < grid_width and 0 <= new_y < grid_height:
      # Check if not in snake body (except tail which will move)
      if (new_x, new_y) not in snake_body[:-1]:
        neighbors.append((new_x, new_y))

  return neighbors


def find_path_astar(start, goal, snake_body, grid_width, grid_height):
  # Initialize frontier with start position
  frontier = PriorityQueue()
  frontier.put(start, 0)

  # Track parent nodes for path reconstruction
  came_from = {start: None}

  # Track cost from start to each node (g score)
  cost_so_far = {start: 0}

  # Limit iterations to prevent infinite loops
  max_iterations = 500
  iterations = 0

  # Main A* loop
  while not frontier.empty() and iterations < max_iterations:
    iterations += 1

    # Get node with lowest f score
    current = frontier.get()

    # Goal reached
    if current == goal:
      break

    # Explore all valid neighbors
    for neighbor in get_neighbors(current, snake_body, grid_width, grid_height):
      # Calculate new cost to reach neighbor
      new_cost = cost_so_far[current] + 1

      # If this path is better than previous
      if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
        cost_so_far[neighbor] = new_cost

        # f = g + h
        # g = actual cost from start
        # h = estimated cost to goal (heuristic)
        priority = new_cost + manhattan_distance(neighbor, goal)

        frontier.put(neighbor, priority)
        came_from[neighbor] = current

  # Check if goal was reached
  if goal not in came_from:
    return None

  # Reconstruct path from goal to start
  path = []
  current = goal
  while current != start:
    path.append(current)
    current = came_from[current]

  path.reverse()
  return path


# ============================================================================
# SECTION 2: GAME LOGIC
# ============================================================================


class GameState:

  def __init__(self, grid_width, grid_height):
    self.grid_width = grid_width
    self.grid_height = grid_height
    self.snake = []
    self.food = None
    self.path = None
    self.score = 0
    self.game_over = False

    self.initialize()

  def initialize(self):
    """Initialize or reset the game"""
    # Start snake in center
    start_x = self.grid_width // 2
    start_y = self.grid_height // 2
    self.snake = [(start_x, start_y)]

    # Generate food
    self.food = self.generate_food()

    # Find initial path
    if self.food:
      self.path = find_path_astar(
          self.snake[-1],
          self.food,
          self.snake,
          self.grid_width,
          self.grid_height,
      )

    self.score = 0
    self.game_over = False

  def generate_food(self):
    """Generate food at random position not occupied by snake"""
    max_attempts = 100
    for _ in range(max_attempts):
      food_x = randint(0, self.grid_width - 1)
      food_y = randint(0, self.grid_height - 1)
      food_pos = (food_x, food_y)

      if food_pos not in self.snake:
        return food_pos

    return None

  def update(self):
    """Update game state for one frame"""
    # Check if we have a valid path
    if self.path is None or len(self.path) == 0:
      print("No path to food - Snake is trapped!")
      self.game_over = True
      return False

    # Get next position from path
    next_pos = self.path.pop(0)

    # Move snake
    self.snake.append(next_pos)

    # Check if ate food
    if next_pos == self.food:
      self.score += 1
      print(f"Score: {self.score}")

      # Generate new food
      self.food = self.generate_food()

      if self.food is None:
        print("Grid filled - You won!")
        self.game_over = True
        return False

      # Find new path
      self.path = find_path_astar(
          self.snake[-1],
          self.food,
          self.snake,
          self.grid_width,
          self.grid_height,
      )

      if self.path is None:
        print("No path to new food!")
        self.game_over = True
        return False
    else:
      # Remove tail if food not eaten
      self.snake.pop(0)

    return True


# ============================================================================
# SECTION 3: GUI AND RENDERING
# ============================================================================

# Initialize Pygame
pygame.init()

# Color definitions
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
EELU_BLUE = (0, 60, 150)
GREEN = (0, 255, 100)
RED = (200, 0, 0)
YELLOW = (255, 220, 0)
GRAY = (40, 40, 40)

# Grid configuration
COLUMNS = 15
ROWS = 15
CELL_SIZE = 30

# Screen dimensions
WIDTH = COLUMNS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE + 80

# Initialize window
screen = display.set_mode([WIDTH, HEIGHT])
display.set_caption("Snake AI - EELU Project")
clock = time.Clock()

# Fonts
title_font = pygame.font.SysFont("Arial", 24, bold=True)
score_font = pygame.font.SysFont("Arial", 18)
info_font = pygame.font.SysFont("Arial", 14)


def draw_header(score):
  """Draw header panel with EELU logo and info"""
  header_rect = pygame.Rect(0, 0, WIDTH, 80)
  draw.rect(screen, GRAY, header_rect)
  draw.rect(screen, EELU_BLUE, header_rect, 3)

  # EELU Logo
  logo_rect = pygame.Rect(15, 15, 120, 50)
  draw.rect(screen, EELU_BLUE, logo_rect, 2)
  eelu_text = title_font.render("EELU", True, EELU_BLUE)
  screen.blit(eelu_text, (40, 20))
  sub_text = info_font.render("AI Project", True, WHITE)
  screen.blit(sub_text, (35, 45))

  # Score
  score_text = score_font.render(f"Score: {score}", True, YELLOW)
  screen.blit(score_text, (WIDTH - 150, 30))

  # Controls
  hint_text = info_font.render("Space: Pause | R: Restart", True, WHITE)
  screen.blit(hint_text, (150, 32))


def draw_game_over(final_score):
  """Draw game over overlay"""
  overlay = pygame.Surface((WIDTH, HEIGHT))
  overlay.set_alpha(200)
  overlay.fill(BLACK)
  screen.blit(overlay, (0, 0))

  # Game Over text
  game_over_font = pygame.font.SysFont("Arial", 48, bold=True)
  game_over_text = game_over_font.render("GAME OVER", True, RED)
  text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
  screen.blit(game_over_text, text_rect)

  # Score
  stats_font = pygame.font.SysFont("Arial", 24)
  score_text = stats_font.render(f"Final Score: {final_score}", True, YELLOW)
  score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
  screen.blit(score_text, score_rect)

  # Restart
  restart_font = pygame.font.SysFont("Arial", 16)
  restart_text = restart_font.render(
      "Press R to Restart or Q to Quit", True, WHITE
  )
  restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
  screen.blit(restart_text, restart_rect)


def draw_pause():
  """Draw pause overlay"""
  pause_font = pygame.font.SysFont("Arial", 36, bold=True)
  pause_text = pause_font.render("PAUSED", True, YELLOW)
  pause_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
  screen.blit(pause_text, pause_rect)


def draw_cell(x, y, color):
  """Draw a single cell"""
  pixel_x = x * CELL_SIZE + 2
  pixel_y = y * CELL_SIZE + 82
  draw.rect(screen, color, (pixel_x, pixel_y, CELL_SIZE - 4, CELL_SIZE - 4))


# ============================================================================
# SECTION 4: MAIN GAME LOOP
# ============================================================================


def main():
  """Main game loop"""
  game_state = GameState(COLUMNS, ROWS)

  done = False
  paused = False

  print("=" * 60)
  print("SNAKE AI - EELU PROJECT")
  print("=" * 60)
  print("Controls: Space = Pause | R = Restart | Q = Quit")
  print("-" * 60)

  # Main loop
  while not done:
    clock.tick(6)

    # Handle events
    for event in pygame.event.get():
      if event.type == QUIT:
        done = True
      elif event.type == KEYDOWN:
        if event.key == K_SPACE:
          paused = not paused
        elif event.key == K_r:
          game_state.initialize()
          print("\nGame Restarted!")
          print("-" * 60)
        elif event.key == K_q:
          done = True

    # Handle pause
    if paused:
      draw_pause()
      display.flip()
      continue

    # Update game
    if not game_state.game_over:
      game_state.update()

    # Draw everything
    screen.fill(BLACK)
    draw_header(game_state.score)

    # Draw path (AI visualization)
    if game_state.path:
      for pos in game_state.path:
        draw_cell(pos[0], pos[1], (60, 0, 0))

    # Draw food
    if game_state.food:
      draw_cell(game_state.food[0], game_state.food[1], GREEN)

    # Draw snake with gradient
    body_length = len(game_state.snake)
    for idx, (x, y) in enumerate(game_state.snake[:-1]):
      intensity = int(100 + (155 * idx / max(body_length - 1, 1)))
      draw_cell(x, y, (intensity, intensity, intensity))

    # Draw snake head
    if game_state.snake:
      head = game_state.snake[-1]
      draw_cell(head[0], head[1], BLUE)

    # Draw game over if needed
    if game_state.game_over:
      draw_game_over(game_state.score)

    display.flip()

  print(f"\nFinal Score: {game_state.score}")
  print("Thanks for playing!")
  pygame.quit()


# Entry point
if __name__ == "__main__":
  main()