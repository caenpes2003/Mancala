import tkinter as tk
from tkinter import messagebox
import random

class MancalaGame:
    """
    Clase que implementa la lógica del juego Mancala (variante Kalah)
    con una representación lineal del tablero:
      - Ínidices 0 a 5: pozos del Jugador 1.
      - Índice 6: almacén (Mancala) del Jugador 1.
      - Ínidices 7 a 12: pozos del Jugador 2.
      - Índice 13: almacén (Mancala) del Jugador 2.
    """

    def __init__(self):
        # Inicializa 4 semillas en cada pozo y 0 en cada almacén.
        self.board = [4] * 14
        self.board[6] = 0    # Almacén Jugador 1
        self.board[13] = 0   # Almacén Jugador 2
        self.current_player = 1  # 1: Jugador 1 (inferior), 2: Jugador 2 (superior)

    def get_valid_moves(self, player):
        if player == 1:
            return [i for i in range(0, 6) if self.board[i] > 0]
        else:
            return [i for i in range(7, 13) if self.board[i] > 0]

    def is_game_over(self):
        # El juego termina cuando todos los pozos de un lado están vacíos.
        side1_empty = all(self.board[i] == 0 for i in range(0, 6))
        side2_empty = all(self.board[i] == 0 for i in range(7, 13))
        return side1_empty or side2_empty

    def collect_remaining(self):
        # Si el juego termina, se recogen las semillas que queden en los pozos a cada almacén.
        for i in range(0, 6):
            self.board[6] += self.board[i]
            self.board[i] = 0
        for i in range(7, 13):
            self.board[13] += self.board[i]
            self.board[i] = 0

    def apply_move(self, pit_index):
        """
        Ejecuta el movimiento elegido para el jugador actual:
          - Se seleccionan las semillas del pozo y se distribuyen en sentido antihorario,
            saltando el almacén del oponente.
          - Si la última semilla cae en el almacén propio, se otorga un turno adicional.
          - Si la última semilla cae en un pozo vacío del lado propio, se realiza la captura
            (si el pozo opuesto tiene semillas).
          - Se verifica si el juego terminó y, de ser así, se recogen las semillas restantes.
        Retorna:
          - extra_turn: True si el jugador obtiene turno extra.
          - msg: mensaje de error o "Juego terminado" en caso de finalizar.
        """
        # Validación inicial de movimiento
        if self.current_player == 1 and pit_index not in range(0, 6):
            return False, "Movimiento inválido para Jugador 1."
        if self.current_player == 2 and pit_index not in range(7, 13):
            return False, "Movimiento inválido para Jugador 2."
        if self.board[pit_index] == 0:
            return False, "El pozo seleccionado está vacío."

        seeds = self.board[pit_index]
        self.board[pit_index] = 0
        pos = pit_index

        # Distribución de semillas en sentido antihorario.
        while seeds > 0:
            pos = (pos + 1) % 14
            # Saltar el almacén del oponente.
            if self.current_player == 1 and pos == 13:
                continue
            if self.current_player == 2 and pos == 6:
                continue
            self.board[pos] += 1
            seeds -= 1

        extra_turn = False

        # Verifica turno extra: última semilla en el almacén del jugador actual.
        if self.current_player == 1 and pos == 6:
            extra_turn = True
        elif self.current_player == 2 and pos == 13:
            extra_turn = True
        else:
            # Verifica captura: si la última semilla cae en un pozo vacío del lado propio,
            # se capturan las semillas del pozo opuesto (si las hay).
            if self.current_player == 1 and pos in range(0, 6) and self.board[pos] == 1:
                opposite = 12 - pos
                if self.board[opposite] > 0:
                    self.board[6] += self.board[opposite] + 1
                    self.board[pos] = 0
                    self.board[opposite] = 0
            elif self.current_player == 2 and pos in range(7, 13) and self.board[pos] == 1:
                opposite = 12 - pos
                if self.board[opposite] > 0:
                    self.board[13] += self.board[opposite] + 1
                    self.board[pos] = 0
                    self.board[opposite] = 0

        # Si se cumple condición de finalización, se recogen las semillas restantes.
        if self.is_game_over():
            self.collect_remaining()
            return True, "Juego terminado"

        # Si no ganó turno extra, se alterna el turno.
        if not extra_turn:
            self.current_player = 2 if self.current_player == 1 else 1

        return extra_turn, None

    def get_winner(self):
        # Retorna 1 si gana el Jugador 1, 2 si gana el Jugador 2, o 0 en caso de empate.
        if self.board[6] > self.board[13]:
            return 1
        elif self.board[13] > self.board[6]:
            return 2
        else:
            return 0

class MancalaGUI:
    """
    Clase que gestiona la interfaz gráfica con Tkinter.
    Se implementa el menú de modos de juego y la visualización del tablero,
    mostrando la distribución de semillas y permitiendo la interacción a través de botones.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Mancala - Interfaz de Juego")
        self.game = None
        self.mode = None  # Modos: "HvH" (Humano vs. Humano), "HvS" (Humano vs. Sintético), "SvS" (Sintético vs. Sintético)
        self.create_menu()

    def create_menu(self):
        # Menú inicial para seleccionar el modo de juego.
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(pady=20)
        
        title = tk.Label(self.menu_frame, text="Seleccione Modo de Juego", font=("Helvetica", 16))
        title.pack(pady=10)
        
        btn_hvh = tk.Button(self.menu_frame, text="Humano vs Humano", width=20, command=lambda: self.start_game("HvH"))
        btn_hvh.pack(pady=5)
        
        btn_hvs = tk.Button(self.menu_frame, text="Humano vs Sintético", width=20, command=lambda: self.start_game("HvS"))
        btn_hvs.pack(pady=5)
        
        btn_svs = tk.Button(self.menu_frame, text="Sintético vs Sintético", width=20, command=lambda: self.start_game("SvS"))
        btn_svs.pack(pady=5)
        
        btn_exit = tk.Button(self.menu_frame, text="Salir", width=20, command=self.root.quit)
        btn_exit.pack(pady=5)

    def start_game(self, mode):
        self.mode = mode
        self.game = MancalaGame()
        self.menu_frame.pack_forget()  # Se oculta el menú
        self.create_board()
        self.update_board()
        self.update_status()

        # Si el modo es Sintético vs Sintético o si en HvS corresponde el turno del sintético,
        # se programa el movimiento automático.
        if self.mode == "SvS":
            self.root.after(1000, self.auto_move)
        if self.mode == "HvS" and self.game.current_player == 2:
            self.root.after(1000, self.auto_move)

    def create_board(self):
        # Se crea la interfaz del tablero.
        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack(pady=20)

        # Fila superior: pozos del Jugador 2 (se muestran en orden inverso: índices 12 a 7)
        self.top_buttons = {}
        for i, pit in enumerate(range(12, 6, -1)):
            btn = tk.Button(self.board_frame, text="", font=("Helvetica", 14), width=5, height=2,
                            command=lambda p=pit: self.pit_clicked(p))
            btn.grid(row=0, column=i+1, padx=5, pady=5)
            self.top_buttons[pit] = btn

        # Fila central: almacén del Jugador 2 (izquierda) y del Jugador 1 (derecha)
        self.store_p2 = tk.Label(self.board_frame, text="", font=("Helvetica", 14),
                                 width=5, height=4, relief="ridge", borderwidth=2)
        self.store_p2.grid(row=0, column=0, rowspan=2, padx=5, pady=5)

        self.store_p1 = tk.Label(self.board_frame, text="", font=("Helvetica", 14),
                                 width=5, height=4, relief="ridge", borderwidth=2)
        self.store_p1.grid(row=0, column=7, rowspan=2, padx=5, pady=5)

        # Fila inferior: pozos del Jugador 1 (índices 0 a 5)
        self.bottom_buttons = {}
        for i, pit in enumerate(range(0, 6)):
            btn = tk.Button(self.board_frame, text="", font=("Helvetica", 14), width=5, height=2,
                            command=lambda p=pit: self.pit_clicked(p))
            btn.grid(row=2, column=i+1, padx=5, pady=5)
            self.bottom_buttons[pit] = btn

        # Etiqueta de estado para mostrar el turno actual y mensajes
        self.status_label = tk.Label(self.root, text="", font=("Helvetica", 14))
        self.status_label.pack(pady=10)

        # Botón para reiniciar el juego
        self.new_game_btn = tk.Button(self.root, text="Nuevo Juego", command=self.reset_game)
        self.new_game_btn.pack(pady=5)

    def update_board(self):
        # Actualiza la visualización del tablero a partir del estado actual de self.game.board.
        if self.game is None:
            return
        board = self.game.board

        # Actualizar los pozos del Jugador 2 (fila superior)
        for pit, btn in self.top_buttons.items():
            btn.config(text=str(board[pit]))
            # Según el modo, se habilitan o deshabilitan los botones
            if self.mode in ["HvH", "HvS"]:
                if self.game.current_player == 2 and self.mode == "HvH":
                    btn.config(state="normal")
                elif self.mode == "HvS":
                    # En modo HvS, se asume que el Jugador 2 es sintético; se deshabilita el click manual.
                    btn.config(state="disabled")
                else:
                    btn.config(state="disabled")
            else:
                btn.config(state="disabled")

        # Actualizar los pozos del Jugador 1 (fila inferior)
        for pit, btn in self.bottom_buttons.items():
            btn.config(text=str(board[pit]))
            if self.mode in ["HvH", "HvS"]:
                if self.game.current_player == 1:
                    btn.config(state="normal")
                else:
                    btn.config(state="disabled")
            else:
                btn.config(state="disabled")

        # Actualizar los almacenes.
        self.store_p1.config(text=str(board[6]))
        self.store_p2.config(text=str(board[13]))

    def update_status(self):
        # Actualiza el mensaje de estado: turno actual o resultado final en caso de terminar el juego.
        if self.game is None:
            return
        if self.game.is_game_over():
            winner = self.game.get_winner()
            if winner == 0:
                status = "Empate."
            else:
                status = f"¡Gana Jugador {winner}!"
            self.status_label.config(text=status)
            # Se deshabilitan los botones de los pozos.
            for btn in list(self.top_buttons.values()) + list(self.bottom_buttons.values()):
                btn.config(state="disabled")
        else:
            self.status_label.config(text=f"Turno: Jugador {self.game.current_player}")

    def pit_clicked(self, pit):
        # Evento cuando un usuario hace clic en un pozo.
        if self.game is None or self.game.is_game_over():
            return

        # En modo Humano vs. Sintético, se ignoran los clics si es el turno del sintético.
        if self.mode == "HvS" and self.game.current_player == 2:
            return

        valid_moves = self.game.get_valid_moves(self.game.current_player)
        if pit not in valid_moves:
            messagebox.showwarning("Movimiento inválido", "Seleccione un pozo válido.")
            return

        extra_turn, msg = self.game.apply_move(pit)
        if msg:
            if msg == "Juego terminado":
                self.update_board()
                self.update_status()
                messagebox.showinfo("Fin del Juego", self.get_result_message())
                return
            else:
                messagebox.showerror("Error", msg)
                return

        self.update_board()
        self.update_status()

        # Si después del movimiento corresponde la jugada al síntético, se programa un movimiento automático.
        if not extra_turn:
            if (self.mode == "HvS" and self.game.current_player == 2) or self.mode == "SvS":
                self.root.after(1000, self.auto_move)

    def auto_move(self):
        # Movimiento automático para el jugador sintético o en modo sintético vs sintético.
        if self.game is None or self.game.is_game_over():
            return
        valid_moves = self.game.get_valid_moves(self.game.current_player)
        if not valid_moves:
            return
        pit = random.choice(valid_moves)
        extra_turn, msg = self.game.apply_move(pit)
        self.update_board()
        self.update_status()
        if msg and msg == "Juego terminado":
            messagebox.showinfo("Fin del Juego", self.get_result_message())
            return
        if not extra_turn:
            if (self.mode == "HvS" and self.game.current_player == 2) or self.mode == "SvS":
                self.root.after(1000, self.auto_move)

    def get_result_message(self):
        # Retorna un mensaje con el resultado final de la partida.
        winner = self.game.get_winner()
        if winner == 0:
            return "El juego terminó en empate."
        else:
            return f"¡El Jugador {winner} gana la partida!"

    def reset_game(self):
        # Reinicia el juego.
        if self.game:
            self.game = MancalaGame()
            self.update_board()
            self.update_status()
            if self.mode == "HvS" and self.game.current_player == 2:
                self.root.after(1000, self.auto_move)
            elif self.mode == "SvS":
                self.root.after(1000, self.auto_move)

if __name__ == "__main__":
    root = tk.Tk()
    app = MancalaGUI(root)
    root.mainloop()
