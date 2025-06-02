import tkinter as tk
from tkinter import messagebox
import random
import copy

# ----------------------------------------------------------------------
#  MODELO: reglas de Kalah (variante de Mancala)
# ----------------------------------------------------------------------
class MancalaGame:
    """
    Representación lineal del tablero:
      0-5   : pozos  J1
      6     : almacén J1
      7-12  : pozos  J2
      13    : almacén J2
    """

    def __init__(self):
        self.board = [4] * 14
        self.board[6] = self.board[13] = 0
        self.current_player = 1                         # 1 = J1, 2 = J2

    # ---------- utilidades -------------------------------------------------
    def clone(self):
        g = MancalaGame()
        g.board = self.board.copy()
        g.current_player = self.current_player
        return g

    def get_valid_moves(self, player):
        rng = range(0, 6) if player == 1 else range(7, 13)
        return [i for i in rng if self.board[i] > 0]

    def is_game_over(self):
        return all(self.board[i] == 0 for i in range(0, 6)) \
            or all(self.board[i] == 0 for i in range(7, 13))

    def collect_remaining(self):
        for i in range(0, 6):
            self.board[6] += self.board[i]
            self.board[i] = 0
        for i in range(7, 13):
            self.board[13] += self.board[i]
            self.board[i] = 0

    # ---------- ejecutar movimiento ----------------------------------------
    def apply_move(self, pit_index):
        # Validaciones básicas
        if self.current_player == 1 and pit_index not in range(0, 6):
            return False, "Movimiento inválido para Jugador 1."
        if self.current_player == 2 and pit_index not in range(7, 13):
            return False, "Movimiento inválido para Jugador 2."
        if self.board[pit_index] == 0:
            return False, "El pozo seleccionado está vacío."

        seeds = self.board[pit_index]
        self.board[pit_index] = 0
        pos = pit_index

        # Siembra antihoraria
        while seeds:
            pos = (pos + 1) % 14
            if self.current_player == 1 and pos == 13:
                continue
            if self.current_player == 2 and pos == 6:
                continue
            self.board[pos] += 1
            seeds -= 1

        extra_turn = ((self.current_player == 1 and pos == 6) or
                      (self.current_player == 2 and pos == 13))

        # Captura
        if not extra_turn:
            if self.current_player == 1 and pos in range(0, 6) and self.board[pos] == 1:
                opp = 12 - pos
                if self.board[opp] > 0:
                    self.board[6] += self.board[opp] + 1
                    self.board[pos] = self.board[opp] = 0
            elif self.current_player == 2 and pos in range(7, 13) and self.board[pos] == 1:
                opp = 12 - pos
                if self.board[opp] > 0:
                    self.board[13] += self.board[opp] + 1
                    self.board[pos] = self.board[opp] = 0

        # Fin de juego
        if self.is_game_over():
            self.collect_remaining()
            return True, "Juego terminado"

        # Cambia turno si no hay extra
        if not extra_turn:
            self.current_player = 2 if self.current_player == 1 else 1
        return extra_turn, None

    def get_winner(self):
        return 1 if self.board[6] > self.board[13] else 2 if self.board[13] > self.board[6] else 0


# ----------------------------------------------------------------------
#  JUGADOR SINTÉTICO: Minimax con poda α-β
# ----------------------------------------------------------------------
class MinimaxAI:
    def __init__(self, game: MancalaGame, player_id: int, depth: int = 6):
        self.game = game          # referencia viva al juego real
        self.player_id = player_id
        self.depth = depth

    # ---------- heurística --------------------------------------------------
    def evaluate(self, g: MancalaGame) -> int:
        # Diferencia en almacenes + media de semillas propias - ajenas
        if self.player_id == 1:
            own_store, opp_store = g.board[6], g.board[13]
            own_pits  = sum(g.board[i] for i in range(0, 6))
            opp_pits  = sum(g.board[i] for i in range(7, 13))
        else:
            own_store, opp_store = g.board[13], g.board[6]
            own_pits  = sum(g.board[i] for i in range(7, 13))
            opp_pits  = sum(g.board[i] for i in range(0, 6))
        return (own_store - opp_store) * 2 + (own_pits - opp_pits)

    # ---------- minimax recursivo -------------------------------------------
    def _minimax(self, g: MancalaGame, depth: int, alpha: int, beta: int, player_turn: int) -> int:
        if depth == 0 or g.is_game_over():
            return self.evaluate(g)

        moves = g.get_valid_moves(player_turn)
        if not moves:                       # sin jugadas; pasa turno
            next_p = 2 if player_turn == 1 else 1
            return self._minimax(g, depth - 1, alpha, beta, next_p)

        maximizing = (player_turn == self.player_id)
        best_val = -float("inf") if maximizing else float("inf")

        for pit in moves:
            new_g = g.clone()
            extra_turn, _ = new_g.apply_move(pit)
            next_p = player_turn if extra_turn else (2 if player_turn == 1 else 1)
            next_depth = depth if extra_turn else depth - 1

            val = self._minimax(new_g, next_depth, alpha, beta, next_p)
            if maximizing:
                best_val = max(best_val, val)
                alpha = max(alpha, val)
            else:
                best_val = min(best_val, val)
                beta = min(beta, val)
            if beta <= alpha:              # poda α-β
                break
        return best_val

    # ---------- interfaz pública --------------------------------------------
    def choose_move(self) -> int:
        best_score = -float("inf")
        best_pit = None
        for pit in self.game.get_valid_moves(self.player_id):
            clone = self.game.clone()
            extra, _ = clone.apply_move(pit)
            next_p = self.player_id if extra else (2 if self.player_id == 1 else 1)
            score = self._minimax(clone, self.depth - 1, -float("inf"), float("inf"), next_p)
            if score > best_score:
                best_score, best_pit = score, pit
        # En casos raros sin mejor, juega aleatorio
        if best_pit is None:
            best_pit = random.choice(self.game.get_valid_moves(self.player_id))
        return best_pit


# ----------------------------------------------------------------------
#  VISTA + CONTROLADOR (Tkinter)
# ----------------------------------------------------------------------
class MancalaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mancala")
        self.game = None
        self.mode = None
        self.ai_p1 = self.ai_p2 = None
        self.create_menu()

    # ---------- menú inicial ------------------------------------------------
    def create_menu(self):
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(pady=20)

        tk.Label(self.menu_frame, text="Seleccione Modo de Juego", font=("Helvetica", 16)).pack(pady=10)

        tk.Button(self.menu_frame, text="Humano vs Humano", width=22,
                  command=lambda: self.start_game("HvH")).pack(pady=4)
        tk.Button(self.menu_frame, text="Humano vs Sintético", width=22,
                  command=lambda: self.start_game("HvS")).pack(pady=4)
        tk.Button(self.menu_frame, text="Sintético vs Sintético", width=22,
                  command=lambda: self.start_game("SvS")).pack(pady=4)
        tk.Button(self.menu_frame, text="Salir", width=22,
                  command=self.root.quit).pack(pady=4)

    # ---------- inicio de partida ------------------------------------------
    def start_game(self, mode):
        self.mode = mode
        self.game = MancalaGame()

        # Instanciar IA según el modo
        self.ai_p1 = self.ai_p2 = None
        if mode == "HvS":
            self.ai_p2 = MinimaxAI(self.game, 2, depth=6)
        elif mode == "SvS":
            self.ai_p1 = MinimaxAI(self.game, 1, depth=6)
            self.ai_p2 = MinimaxAI(self.game, 2, depth=6)

        self.menu_frame.pack_forget()
        self.create_board()
        self.update_board()
        self.update_status()

        # Turno automático inicial si corresponde
        if (mode == "HvS" and self.game.current_player == 2) or mode == "SvS":
            self.root.after(600, self.auto_move)

    # ---------- construcción de GUI ----------------------------------------
    def create_board(self):
        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack(pady=10)

        # Fila superior (J2) 12-7
        self.top_btn = {}
        for col, pit in enumerate(range(12, 6, -1), start=1):
            b = tk.Button(self.board_frame, width=5, height=2,
                          command=lambda p=pit: self.pit_clicked(p))
            b.grid(row=0, column=col, padx=4, pady=4)
            self.top_btn[pit] = b

        # Almacenes
        self.store_p2 = tk.Label(self.board_frame, width=5, height=4, relief="ridge")
        self.store_p2.grid(row=0, column=0, rowspan=2, padx=4)
        self.store_p1 = tk.Label(self.board_frame, width=5, height=4, relief="ridge")
        self.store_p1.grid(row=0, column=7, rowspan=2, padx=4)

        # Fila inferior (J1) 0-5
        self.bot_btn = {}
        for col, pit in enumerate(range(0, 6), start=1):
            b = tk.Button(self.board_frame, width=5, height=2,
                          command=lambda p=pit: self.pit_clicked(p))
            b.grid(row=2, column=col, padx=4, pady=4)
            self.bot_btn[pit] = b

        self.status = tk.Label(self.root, font=("Helvetica", 14))
        self.status.pack(pady=6)

        self.new_btn = tk.Button(self.root, text="Nuevo Juego", command=self.reset_game)
        self.new_btn.pack(pady=4)

    # ---------- refresco ----------------------------------------------------
    def update_board(self):
        if not self.game:
            return
        bd = self.game.board
        # pozos J2
        for pit, btn in self.top_btn.items():
            btn.config(text=str(bd[pit]))
            btn.config(state=("normal" if self.mode == "HvH" and self.game.current_player == 2 else "disabled"))
        # pozos J1
        for pit, btn in self.bot_btn.items():
            btn.config(text=str(bd[pit]))
            btn.config(state=("normal" if self.game.current_player == 1 and self.mode != "SvS" else "disabled"))
        # almacenes
        self.store_p1.config(text=str(bd[6]))
        self.store_p2.config(text=str(bd[13]))

    def update_status(self):
        if self.game.is_game_over():
            w = self.game.get_winner()
            txt = "Empate." if w == 0 else f"¡Gana Jugador {w}!"
        else:
            txt = f"Turno: Jugador {self.game.current_player}"
        self.status.config(text=txt)

    # ---------- interacción -------------------------------------------------
    def pit_clicked(self, pit):
        if self.mode == "HvS" and self.game.current_player == 2:
            return
        valid = self.game.get_valid_moves(self.game.current_player)
        if pit not in valid:
            messagebox.showwarning("Movimiento inválido", "Seleccione un pozo válido.")
            return

        extra, msg = self.game.apply_move(pit)
        self.update_board()
        self.update_status()

        if msg:
            messagebox.showinfo("Fin del Juego", self.result_msg())
            return

        if not extra:
            self.root.after(600, self.auto_move)

    # ---------- IA / turnos automáticos ------------------------------------
    def auto_move(self):
        if self.game.is_game_over():
            messagebox.showinfo("Fin del Juego", self.result_msg())
            return

        player = self.game.current_player
        ai = self.ai_p1 if player == 1 else self.ai_p2
        pit = ai.choose_move() if ai else random.choice(self.game.get_valid_moves(player))
        print(f"IA J{player} elige pozo {pit}")  # trazas de depuración

        extra, _ = self.game.apply_move(pit)
        self.update_board()
        self.update_status()

        if self.game.is_game_over():
            messagebox.showinfo("Fin del Juego", self.result_msg())
        else:
            # programa otro turno si aún manda la IA
            if (self.mode == "SvS") or (self.mode == "HvS" and self.game.current_player == 2):
                self.root.after(600, self.auto_move)

    # ---------- utilidades --------------------------------------------------
    def result_msg(self):
        w = self.game.get_winner()
        return "Empate." if w == 0 else f"¡El Jugador {w} gana la partida!"

    def reset_game(self):
        self.start_game(self.mode)


# ----------------------------------------------------------------------
#  MAIN
# ----------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    MancalaGUI(root)
    root.mainloop()
