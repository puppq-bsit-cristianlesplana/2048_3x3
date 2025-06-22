# Example integration in adventure_mode.py or swift_mode.py
from level_system import show_level_complete_message, check_level_completion

def run_adventure_mode(screen, font):
    # ... existing code ...
    
    current_level = 1
    target_score = level_targets[current_level]['score']
    target_tile = level_targets[current_level]['tile']
    
    def proceed_to_next_level():
        nonlocal current_level, grid, score, target_score, target_tile
        current_level += 1
        if current_level <= max_level:
            # Initialize the next level
            grid = initialize_grid(3)
            grid = add_new_tile(grid)
            grid = add_new_tile(grid)
            score = 0
            target_score = level_targets[current_level]['score']
            target_tile = level_targets[current_level]['tile']
        else:
            # Game completed
            return "home"
    
    # ... existing game loop code ...
    
    while True:
        # ... existing event handling and drawing ...
        
        # Check for level completion
        if check_level_completion(grid, score, target_score, target_tile):
            # Show completion message and proceed to next level
            if not show_level_complete_message(screen, font, current_level, proceed_to_next_level):
                return "home"  # User quit during the message
        
        # ... rest of the game loop ...