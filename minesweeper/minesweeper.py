import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # Si el número de minas conocido es igual al número de celdas en la sentencia, todas las celdas son minas.
        if self.count == len(self.cells):
            return self.cells.copy()
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # Si el número de minas conocido es 0, todas las celdas son seguras.
        if self.count == 0:
            return self.cells.copy()
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            # La celda es una mina, por lo que debe ser eliminada de la sentencia.
            self.cells.remove(cell)
            # Se reduce el número de minas conocido en la sentencia.
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            # La celda es segura, por lo que debe ser eliminada de la sentencia.
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        i, j = cell

        # 1) Marcar la celda como un movimiento realizado
        self.moves_made.add(cell)

        # 2) Marcar la celda como segura
        self.mark_safe(cell)

        # 3) Agregar una nueva sentencia a la base de conocimientos
        # para indicar que count de los vecinos de cell son minas
        neighbors = []
        for x in range(max(0, i - 1), min(self.height, i + 2)):
            for y in range(max(0, j - 1), min(self.width, j + 2)):
                neighbor = (x, y)
                if neighbor != cell and neighbor not in self.safes:
                    neighbors.append(neighbor)

        new_sentence = Sentence(neighbors, count)
        self.knowledge.append(new_sentence)

       # 4) y 5) Actualizar celdas como seguras o minas según la nueva información
        for sentence in self.knowledge:
            known_mines = sentence.known_mines()
            known_safes = sentence.known_safes()
            if known_mines:
                for mine in known_mines.copy():
                    self.mark_mine(mine)
            if known_safes:
                for safe in known_safes.copy():
                    self.mark_safe(safe)

        # 5) Agregar nuevas sentencias si se pueden inferir
        new_knowledge = []
        for sentence1 in self.knowledge:
            for sentence2 in self.knowledge:
                if sentence1 != sentence2:
                    if sentence1.cells.issubset(sentence2.cells):
                        new_cells = sentence2.cells - sentence1.cells
                        new_count = sentence2.count - sentence1.count
                        new_sentence = Sentence(new_cells, new_count)
                        if new_sentence not in self.knowledge and new_sentence not in new_knowledge:
                            new_knowledge.append(new_sentence)
        # Actualizar celdas vecinas de 'cell' si es posible deducir información
        for sentence in new_knowledge:
            for neighbor in sentence.cells.copy():
                if neighbor != cell:
                    if neighbor not in self.mines and neighbor not in self.safes:
                        if sentence.count == 0:
                            self.mark_safe(neighbor)
                        elif sentence.count == len(sentence.cells):
                            self.mark_mine(neighbor)
        self.knowledge.extend(new_knowledge)


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for i in range(self.height):
            for j in range(self.width):
                cell = (i, j)
                # Verificar si la celda es segura y no ha sido movida
                if cell not in self.moves_made and cell in self.safes:
                    return cell
        return None  # No se encontró un movimiento seguro

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        possible_moves = []
        for i in range(self.height):
            for j in range(self.width):
                cell = (i, j)
                # Verificar si la celda no ha sido movida y no es una mina conocida
                if cell not in self.moves_made and cell not in self.mines:
                    possible_moves.append(cell)
        
        if possible_moves:
            return random.choice(possible_moves)  # Aleatorio
        else:
            return None  # Si no hay aletorio
