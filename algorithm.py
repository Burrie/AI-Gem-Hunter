def is_trap(grid, i, j):
    if grid[i][j] == 'T':
        return True
    if grid[i][j] == 'G':
        return False
    
    count_traps = 0
    for x in range(max(0, i - 1), min(len(grid), i + 2)):
        for y in range(max(0, j - 1), min(len(grid[i]), j + 2)):
            if grid[x][y] == 'T':
                count_traps += 1
    return count_traps == int(grid[i][j])

def brute_force(grid):
    result = [['_' for _ in row] for row in grid]
    
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if is_trap(grid, i, j):
                result[i][j] = 'T'
            else:
                result[i][j] = 'G'
    
    return result

def is_valid(grid, i, j):
    return i >= 0 and i < len(grid) and j >= 0 and j < len(grid[i])

def backtracking(grid, row, col):
    if row == len(grid):
        return True

    next_row = row
    next_col = col + 1
    if next_col == len(grid[row]):
        next_row += 1
        next_col = 0

    if grid[row][col] == '_':
        grid[row][col] = 'G'
        if is_trap(grid, row, col):
            grid[row][col] = 'T'
            if not backtracking(grid, next_row, next_col):
                grid[row][col] = '_'
                return False
        else:
            if not backtracking(grid, next_row, next_col):
                grid[row][col] = '_'
                return False
            grid[row][col] = 'G'
    else:
        if not backtracking(grid, next_row, next_col):
            return False
    return True

def backtracking_solve(grid):
    backtracking(grid, 0, 0)
    return grid