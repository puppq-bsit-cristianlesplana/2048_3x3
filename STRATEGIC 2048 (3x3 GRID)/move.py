import random
merge_callback = None

def set_merge_callback(callback):
    """Set a callback function to be called when tiles are merged"""
    global merge_callback
    merge_callback = callback

def initialize_grid(size=4):
    return [[0 for _ in range(size)] for _ in range(size)]
def add_new_tile(grid):
    size = len(grid)
    empty_cells = [(i, j) for i in range(size) for j in range(size) if grid[i][j] == 0]
    if not empty_cells:
        return grid
    i, j = random.choice(empty_cells)
    grid[i][j] = 2 if random.random() < 0.9 else 4
    return grid
def merge_row_left(row):
    """Merge a row to the left and track merges"""
    global merge_callback
    new_row = [num for num in row if num != 0]
    score = 0
    i = 0
    while i < len(new_row) - 1:
        if new_row[i] == new_row[i + 1]:
            merged_value = new_row[i] * 2
            new_row[i] = merged_value
            score += merged_value
            
            # Call the callback to track the merge
            if merge_callback:
                merge_callback(merged_value)
            
            new_row.pop(i + 1)
        i += 1
    new_row += [0] * (len(row) - len(new_row))
    return new_row, score

def move_left(grid):
    new_grid = []
    total_score = 0
    moved = False
    for row in grid:
        original_row = row[:]
        new_row, score = merge_row_left(row)
        if new_row != original_row:
            moved = True
        new_grid.append(new_row)
        total_score += score
    return new_grid, moved, total_score

def move_right(grid):
    new_grid = []
    total_score = 0
    moved = False
    for row, original_row in zip(grid, grid):
        reversed_row = row[::-1]
        new_row, score = merge_row_left(reversed_row)
        new_row = new_row[::-1]
        if new_row != original_row:
            moved = True
        new_grid.append(new_row)
        total_score += score
    return new_grid, moved, total_score

def transpose(grid):
    return [list(row) for row in zip(*grid)]

def move_up(grid):
    transposed = transpose(grid)
    moved_grid, moved, score = move_left(transposed)
    return transpose(moved_grid), moved, score

def move_down(grid):
    transposed = transpose(grid)
    moved_grid, moved, score = move_right(transposed)
    return transpose(moved_grid), moved, score

def can_move(grid):
    for row in grid:
        if 0 in row:
            return True
    for row in grid:
        for i in range(len(row) - 1):
            if row[i] == row[i + 1]:
                return True
    for j in range(len(grid)):
        for i in range(len(grid) - 1):
            if grid[i][j] == grid[i + 1][j]:
                return True
    return False

def game_over(grid):
    for row in grid:
        if 0 in row:
            return False
    size = len(grid)
    for r in range(size):
        for c in range(size):
            if c + 1 < size and grid[r][c] == grid[r][c + 1]:
                return False
            if r + 1 < size and grid[r][c] == grid[r + 1][c]:
                return False

    return True
