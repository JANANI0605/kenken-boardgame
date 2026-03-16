"""
KenKen Puzzle — Pygame Edition
================================
Install:  pip install pygame
Run:      python kenken_pygame.py
"""

import pygame
import sys
import random
import time

# ──────────────────────────────────────────────
#  COLOURS
# ──────────────────────────────────────────────
BG          = (13,  13,  20)
SURFACE     = (26,  26,  40)
BORDER      = (46,  46,  66)
ACCENT      = (245, 197,  66)   # yellow
TEXT        = (240, 238, 232)
MUTED       = (120, 120, 120)
BLUE_VAL    = (160, 207, 255)
GREEN       = (111, 207, 151)
RED         = (235,  87,  87)
CAGE_BORDER = (245, 197,  66)
SELECTED_BG = (42,  42,  68)
CORRECT_BG  = (21,  37,  21)
WRONG_BG    = (42,  21,  21)
BTN_BG      = (245, 197,  66)
BTN_TEXT    = (13,  13,  20)
BTN2_BG     = (26,  26,  40)
BTN2_BORDER = (80,  80, 100)
NUMPAD_BG   = (26,  26,  40)
NUMPAD_HV   = (42,  42,  68)
WIN_OVERLAY = (13,  13,  20, 220)


# ──────────────────────────────────────────────
#  PUZZLE LOGIC
# ──────────────────────────────────────────────
def latin_square(n):
    g = [[ (r+c)%n+1 for c in range(n)] for r in range(n)]
    for i in range(n-1, 0, -1):
        j = random.randint(0, i)
        g[i], g[j] = g[j], g[i]
    for i in range(n-1, 0, -1):
        j = random.randint(0, i)
        for r in range(n):
            g[r][i], g[r][j] = g[r][j], g[r][i]
    return g


def build_cages(sol, n, diff):
    assigned = [[-1]*n for _ in range(n)]
    cages = []
    cid = 0
    max_sz = 2 if diff == 'Easy' else 3 if diff == 'Medium' else 4

    all_cells = [(r, c) for r in range(n) for c in range(n)]
    random.shuffle(all_cells)

    def neighbors(r, c):
        return [(r+dr, c+dc) for dr,dc in [(-1,0),(1,0),(0,-1),(0,1)]
                if 0 <= r+dr < n and 0 <= c+dc < n]

    for sr, sc in all_cells:
        if assigned[sr][sc] >= 0:
            continue
        cells = [(sr, sc)]
        assigned[sr][sc] = cid
        sz = random.randint(1, max_sz)
        for _ in range(sz - 1):
            cands = [(nr,nc) for r,c in cells
                     for nr,nc in neighbors(r,c)
                     if assigned[nr][nc] < 0]
            if not cands:
                break
            pick = random.choice(cands)
            cells.append(pick)
            assigned[pick[0]][pick[1]] = cid

        vals = [sol[r][c] for r,c in cells]
        op, target = '', 0

        if len(cells) == 1:
            target = vals[0]
        else:
            allowed = ['+', '-'] if diff == 'Easy' else \
                      ['+', '-', '×'] if diff == 'Medium' else \
                      ['+', '-', '×', '÷']
            possible = ['+']
            if len(cells) == 2:
                possible += ['-', '×']
                a, b = max(vals), min(vals)
                if b != 0 and a % b == 0:
                    possible.append('÷')
            else:
                possible.append('×')
            choices = [o for o in allowed if o in possible]
            op = random.choice(choices) if choices else '+'

            if op == '+':
                target = sum(vals)
            elif op == '×':
                t = 1
                for v in vals: t *= v
                target = t
            elif op == '-':
                sv = sorted(vals, reverse=True)
                target = sv[0] - sum(sv[1:])
                if target < 1:
                    op = '+'; target = sum(vals)
            elif op == '÷':
                sv = sorted(vals, reverse=True)
                t = sv[0]
                ok = True
                for v in sv[1:]:
                    if v != 0 and t % v == 0:
                        t //= v
                    else:
                        ok = False; break
                if ok and t >= 1:
                    target = t
                else:
                    op = '×'
                    t = 1
                    for v in vals: t *= v
                    target = t

        top_cell = sorted(cells)[0]
        cages.append({'id': cid, 'cells': cells, 'op': op,
                      'target': target, 'top': top_cell})
        cid += 1

    return cages


def make_puzzle(n, diff):
    sol = latin_square(n)
    cages = build_cages(sol, n, diff)
    return {'sol': sol, 'cages': cages, 'n': n}


# ──────────────────────────────────────────────
#  BUTTON
# ──────────────────────────────────────────────
class Button:
    def __init__(self, rect, label, primary=True):
        self.rect   = pygame.Rect(rect)
        self.label  = label
        self.primary = primary
        self.hovered = False

    def draw(self, surf, font):
        bg = BTN_BG if self.primary else (NUMPAD_HV if self.hovered else BTN2_BG)
        pygame.draw.rect(surf, bg, self.rect, border_radius=6)
        if not self.primary:
            pygame.draw.rect(surf, BTN2_BORDER if not self.hovered else ACCENT,
                             self.rect, 1, border_radius=6)
        tc = BTN_TEXT if self.primary else (ACCENT if self.hovered else TEXT)
        txt = font.render(self.label, True, tc)
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def handle(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


# ──────────────────────────────────────────────
#  DROPDOWN
# ──────────────────────────────────────────────
class Dropdown:
    def __init__(self, rect, options, selected=0):
        self.rect     = pygame.Rect(rect)
        self.options  = options
        self.selected = selected
        self.open     = False

    @property
    def value(self):
        return self.options[self.selected]

    def draw(self, surf, font):
        pygame.draw.rect(surf, SURFACE, self.rect, border_radius=4)
        pygame.draw.rect(surf, ACCENT if self.open else BORDER,
                         self.rect, 1, border_radius=4)
        txt = font.render(self.value, True, TEXT)
        surf.blit(txt, (self.rect.x+10, self.rect.y + (self.rect.h-txt.get_height())//2))
        arr = font.render('▾', True, ACCENT)
        surf.blit(arr, (self.rect.right-22, self.rect.y+(self.rect.h-arr.get_height())//2))

        if self.open:
            item_h = self.rect.h
            for i, opt in enumerate(self.options):
                r = pygame.Rect(self.rect.x,
                                self.rect.bottom + i*item_h,
                                self.rect.w, item_h)
                bg = SELECTED_BG if i == self.selected else SURFACE
                pygame.draw.rect(surf, bg, r)
                pygame.draw.rect(surf, BORDER, r, 1)
                t = font.render(opt, True, ACCENT if i == self.selected else TEXT)
                surf.blit(t, (r.x+10, r.y+(r.h-t.get_height())//2))

    def handle(self, event):
        changed = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.open = not self.open
            elif self.open:
                item_h = self.rect.h
                for i in range(len(self.options)):
                    r = pygame.Rect(self.rect.x,
                                    self.rect.bottom + i*item_h,
                                    self.rect.w, item_h)
                    if r.collidepoint(event.pos):
                        self.selected = i
                        changed = True
                        break
                self.open = False
        return changed


# ──────────────────────────────────────────────
#  MAIN GAME
# ──────────────────────────────────────────────
class KenKen:
    SIZES = ['3×3', '4×4', '5×5', '6×6']
    DIFFS = ['Easy', 'Medium', 'Hard']

    def __init__(self):
        pygame.init()
        self.W, self.H = 900, 680
        self.screen = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
        pygame.display.set_caption('KenKen Puzzle')

        # fonts
        self.font_lg  = pygame.font.SysFont('consolas,couriernew,monospace', 36, bold=True)
        self.font_md  = pygame.font.SysFont('consolas,couriernew,monospace', 20, bold=True)
        self.font_sm  = pygame.font.SysFont('consolas,couriernew,monospace', 14)
        self.font_btn = pygame.font.SysFont('consolas,couriernew,monospace', 15, bold=True)
        self.font_hint= pygame.font.SysFont('consolas,couriernew,monospace', 12, bold=True)

        # dropdowns
        self.dd_size = Dropdown((20, 14, 110, 34), self.SIZES, selected=1)
        self.dd_diff = Dropdown((150, 14, 110, 34), self.DIFFS, selected=1)

        # buttons
        self.btn_gen   = Button((280, 14, 110, 34), 'Generate', primary=True)
        self.btn_check = Button((400, 14, 90,  34), 'Check',    primary=False)
        self.btn_solve = Button((500, 14, 90,  34), 'Solve',    primary=False)
        self.btn_new   = Button((340, 420, 160, 44), 'New Puzzle', primary=True)

        self.puzzle   = None
        self.user     = []
        self.sel      = None
        self.state    = {}  # (r,c) -> 'ok'|'err'|None
        self.start_t  = None
        self.elapsed  = 0
        self.moves    = 0
        self.won      = False
        self.status   = 'Press Generate to start'
        self.status_c = MUTED

        self.cell_size = 80
        self.grid_ox   = 0
        self.grid_oy   = 0

        self.clock = pygame.time.Clock()

    # ── layout ──────────────────────────────
    def layout(self):
        W, H = self.screen.get_size()
        n = self.puzzle['n'] if self.puzzle else 4

        # right panel width: numpad cols * (btn+gap) + info padding
        PANEL_W = 240
        MARGIN   = 20

        # cell size fills available space left of right panel, centred
        avail_w = W - PANEL_W - MARGIN * 3   # space for grid
        avail_h = H - 80                      # below toolbar
        max_cell = min(avail_w // n, avail_h // n, 90)
        self.cell_size = max(50, max_cell)

        grid_w = self.cell_size * n
        grid_h = self.cell_size * n

        # centre the grid in the left region
        left_region_w = W - PANEL_W - MARGIN
        self.grid_ox = (left_region_w - grid_w) // 2
        self.grid_oy = 70 + (avail_h - grid_h) // 2

        # right panel starts after the left region
        self.panel_x = W - PANEL_W - MARGIN

        # reposition toolbar buttons (centred in left region)
        total_btn_w = sum(b.rect.w for b in [self.btn_gen, self.btn_check, self.btn_solve]) + 20
        bx = (left_region_w - total_btn_w) // 2
        for btn in [self.btn_gen, self.btn_check, self.btn_solve]:
            btn.rect.x = bx; bx += btn.rect.w + 10

    # ── drawing ─────────────────────────────
    def draw_header(self):
        W = self.screen.get_width()
        # Logo
        logo1 = self.font_lg.render('KEN', True, TEXT)
        logo2 = self.font_lg.render('KEN', True, ACCENT)
        lw = logo1.get_width() + logo2.get_width()
        # Put logo at far right
        lx = W - lw - 20
        self.screen.blit(logo1, (lx, 10))
        self.screen.blit(logo2, (lx + logo1.get_width(), 10))

    def draw_status(self):
        txt = self.font_sm.render(self.status, True, self.status_c)
        W = self.screen.get_width()
        logo1 = self.font_lg.render('KEN', True, TEXT)
        logo2 = self.font_lg.render('KEN', True, ACCENT)
        lw = logo1.get_width() + logo2.get_width()
        lx = W - lw - 20
        TAB = 24
        self.screen.blit(txt, (lx - txt.get_width() - TAB, 22))

    def draw_grid(self):
        if not self.puzzle:
            msg = self.font_md.render('Press  Generate  to start', True, MUTED)
            W, H = self.screen.get_size()
            self.screen.blit(msg, msg.get_rect(center=(self.panel_x // 2, H // 2)))
            return

        p  = self.puzzle
        n  = p['n']
        cs = self.cell_size
        ox, oy = self.grid_ox, self.grid_oy

        cage_of = [[None]*n for _ in range(n)]
        for cage in p['cages']:
            for r,c in cage['cells']:
                cage_of[r][c] = cage

        for r in range(n):
            for c in range(n):
                x = ox + c*cs
                y = oy + r*cs
                rect = pygame.Rect(x, y, cs, cs)

                # background
                bg = SURFACE
                if self.sel == (r,c):       bg = SELECTED_BG
                if (r,c) in self.state:
                    s = self.state[(r,c)]
                    if s == 'ok':  bg = CORRECT_BG
                    if s == 'err': bg = WRONG_BG
                pygame.draw.rect(self.screen, bg, rect)

                # inner grid line
                pygame.draw.rect(self.screen, BORDER, rect, 1)

                # cage borders (thick yellow)
                cage = cage_of[r][c]
                if cage:
                    def in_cage(dr,dc):
                        return any(cr==r+dr and cc==c+dc for cr,cc in cage['cells'])
                    bw = 3
                    if not in_cage(-1,0):
                        pygame.draw.line(self.screen, CAGE_BORDER, (x,y),   (x+cs,y),   bw)
                    if not in_cage(1,0):
                        pygame.draw.line(self.screen, CAGE_BORDER, (x,y+cs),(x+cs,y+cs),bw)
                    if not in_cage(0,-1):
                        pygame.draw.line(self.screen, CAGE_BORDER, (x,y),   (x,y+cs),   bw)
                    if not in_cage(0,1):
                        pygame.draw.line(self.screen, CAGE_BORDER, (x+cs,y),(x+cs,y+cs),bw)

                    # hint label on top-left cell of cage
                    if (r,c) == cage['top']:
                        label = f"{cage['target']}{cage['op']}"
                        ht = self.font_hint.render(label, True, ACCENT)
                        self.screen.blit(ht, (x+4, y+3))

                # user value
                v = self.user[r][c]
                if v:
                    col = BLUE_VAL
                    if (r,c) in self.state:
                        col = GREEN if self.state[(r,c)]=='ok' else RED
                    num = self.font_md.render(str(v), True, col)
                    self.screen.blit(num, num.get_rect(center=(x+cs//2, y+cs//2)))

        # outer border
        outer = pygame.Rect(ox, oy, n*cs, n*cs)
        pygame.draw.rect(self.screen, ACCENT, outer, 3)

    def draw_numpad(self):
        if not self.puzzle:
            return
        n  = self.puzzle['n']
        px = self.panel_x
        py = self.grid_oy

        title = self.font_sm.render('NUMBERS', True, MUTED)
        self.screen.blit(title, (px, py))
        py += 24

        cols = min(n, 4)
        bsz  = 48
        gap  = 6
        for i in range(1, n+1):
            col = (i-1) % cols
            row = (i-1) // cols
            x = px + col*(bsz+gap)
            y = py + row*(bsz+gap)
            r = pygame.Rect(x, y, bsz, bsz)
            mx,my = pygame.mouse.get_pos()
            hv = r.collidepoint(mx,my)
            pygame.draw.rect(self.screen, NUMPAD_HV if hv else NUMPAD_BG, r, border_radius=4)
            pygame.draw.rect(self.screen, ACCENT if hv else BORDER, r, 1, border_radius=4)
            t = self.font_md.render(str(i), True, ACCENT if hv else TEXT)
            self.screen.blit(t, t.get_rect(center=r.center))

        # erase
        rows = (n-1)//cols + 1
        ey = py + rows*(bsz+gap) + 4
        er = pygame.Rect(px, ey, cols*(bsz+gap)-gap, 32)
        mx,my = pygame.mouse.get_pos()
        hv = er.collidepoint(mx,my)
        pygame.draw.rect(self.screen, NUMPAD_HV if hv else NUMPAD_BG, er, border_radius=4)
        pygame.draw.rect(self.screen, (200,80,80) if hv else BORDER, er, 1, border_radius=4)
        et = self.font_sm.render('⌫  ERASE', True, RED if hv else MUTED)
        self.screen.blit(et, et.get_rect(center=er.center))

        self._numpad_y   = py
        self._numpad_bsz = bsz
        self._numpad_gap = gap
        self._numpad_cols= cols
        self._numpad_rows= rows
        self._erase_rect = er

    def draw_info(self):
        if not self.puzzle:
            return
        px = self.panel_x
        n  = self.puzzle['n']
        cols = min(n,4); bsz=48; gap=6
        rows = (n-1)//cols+1
        py = self.grid_oy + 24 + rows*(bsz+gap) + 42 + 20

        # box
        iw = cols*(bsz+gap)-gap + 20
        panel = pygame.Rect(px-10, py, iw, 180)
        pygame.draw.rect(self.screen, SURFACE, panel, border_radius=8)
        pygame.draw.rect(self.screen, BORDER,  panel, 1, border_radius=8)

        title = self.font_sm.render('SESSION', True, MUTED)
        self.screen.blit(title, (px, py+10))

        elapsed = self.elapsed
        if self.start_t and not self.won:
            elapsed = int(time.time() - self.start_t)
        m = elapsed//60; s = elapsed%60
        tstr = f'{m}m {s}s' if m else f'{s}s'

        rows_info = [
            ('Time',   tstr,              ACCENT),
            ('Moves',  str(self.moves),   ACCENT),
            ('Grid',   f'{n}×{n}',        ACCENT),
            ('Cages',  str(len(self.puzzle["cages"])), ACCENT),
            ('Diff',   self.dd_diff.value,
             GREEN if self.dd_diff.value=='Easy'
             else ACCENT if self.dd_diff.value=='Medium' else RED),
        ]
        for i,(lbl,val,vc) in enumerate(rows_info):
            ry = py + 34 + i*28
            lt = self.font_sm.render(lbl, True, MUTED)
            vt = self.font_sm.render(val, True, vc)
            self.screen.blit(lt, (px, ry))
            self.screen.blit(vt, (px + iw - vt.get_width() - 20, ry))

    def draw_win(self):
        W, H = self.screen.get_size()
        overlay = pygame.Surface((W,H), pygame.SRCALPHA)
        overlay.fill((13,13,20,220))
        self.screen.blit(overlay, (0,0))

        star = self.font_lg.render('★  Puzzle Solved!  ★', True, ACCENT)
        self.screen.blit(star, star.get_rect(center=(W//2, H//2 - 80)))

        elapsed = self.elapsed
        m=elapsed//60; s=elapsed%60
        tstr=f'{m}m {s}s' if m else f'{s}s'
        sub = self.font_md.render(
            f'Solved in {tstr}  ·  {self.moves} moves', True, MUTED)
        self.screen.blit(sub, sub.get_rect(center=(W//2, H//2-30)))

        self.btn_new.rect.center = (W//2, H//2+50)
        self.btn_new.draw(self.screen, self.font_btn)

    # ── interaction ─────────────────────────
    def select_cell(self, r, c):
        self.sel = (r,c)

    def input_num(self, num):
        if not self.sel or not self.puzzle:
            return
        r,c = self.sel
        self.user[r][c] = num
        self.moves += 1
        self.state.pop((r,c), None)
        self.auto_win()

    def auto_win(self):
        n = self.puzzle['n']
        for r in range(n):
            for c in range(n):
                if self.user[r][c] == 0:
                    return
        sol = self.puzzle['sol']
        for r in range(n):
            for c in range(n):
                if self.user[r][c] != sol[r][c]:
                    return
        self.won = True
        self.elapsed = int(time.time() - self.start_t)

    def check_puzzle(self):
        if not self.puzzle:
            return
        sol = self.puzzle['sol']
        n   = self.puzzle['n']
        good = bad = 0
        self.state.clear()
        for r in range(n):
            for c in range(n):
                v = self.user[r][c]
                if not v:
                    continue
                if v == sol[r][c]:
                    self.state[(r,c)] = 'ok'; good+=1
                else:
                    self.state[(r,c)] = 'err'; bad+=1
        self.status = f'✓ {good}  correct    ✗ {bad}  wrong'
        self.status_c = GREEN if bad==0 else RED

    def solve_puzzle(self):
        if not self.puzzle:
            return
        sol = self.puzzle['sol']
        n   = self.puzzle['n']
        for r in range(n):
            for c in range(n):
                self.user[r][c] = sol[r][c]
                self.state[(r,c)] = 'ok'
        self.won = True
        self.elapsed = int(time.time() - self.start_t)
        self.status = 'Solved!'; self.status_c = GREEN

    def generate(self):
        n = int(self.dd_size.value[0])
        d = self.dd_diff.value
        self.puzzle  = make_puzzle(n, d)
        self.user    = [[0]*n for _ in range(n)]
        self.sel     = None
        self.state   = {}
        self.won     = False
        self.moves   = 0
        self.start_t = time.time()
        self.elapsed = 0
        self.status  = 'Playing'
        self.status_c= GREEN
        self.layout()

    def handle_grid_click(self, mx, my):
        if not self.puzzle:
            return
        n  = self.puzzle['n']
        cs = self.cell_size
        ox, oy = self.grid_ox, self.grid_oy
        if ox <= mx < ox+n*cs and oy <= my < oy+n*cs:
            c = (mx-ox)//cs
            r = (my-oy)//cs
            self.select_cell(r,c)

    def handle_numpad_click(self, mx, my):
        if not self.puzzle:
            return
        if not hasattr(self,'_numpad_y'):
            return
        px   = self.panel_x
        py   = self._numpad_y
        bsz  = self._numpad_bsz
        gap  = self._numpad_gap
        cols = self._numpad_cols
        n    = self.puzzle['n']
        for i in range(1, n+1):
            col = (i-1)%cols; row=(i-1)//cols
            x=px+col*(bsz+gap); y=py+row*(bsz+gap)
            r=pygame.Rect(x,y,bsz,bsz)
            if r.collidepoint(mx,my):
                self.input_num(i); return
        if self._erase_rect.collidepoint(mx,my):
            self.input_num(0)

    # ── main loop ───────────────────────────
    def run(self):
        self.layout()
        while True:
            self.screen.fill(BG)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if event.type == pygame.VIDEORESIZE:
                    self.layout()

                # dropdowns
                for dd in [self.dd_size, self.dd_diff]:
                    dd.handle(event)

                # buttons
                if self.btn_gen.handle(event):
                    self.generate()
                if self.btn_check.handle(event):
                    self.check_puzzle()
                if self.btn_solve.handle(event):
                    self.solve_puzzle()
                if self.won and self.btn_new.handle(event):
                    self.generate()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # close dropdowns on outside click (already handled)
                    self.handle_grid_click(*event.pos)
                    self.handle_numpad_click(*event.pos)

                if event.type == pygame.KEYDOWN:
                    k = event.key
                    n = self.puzzle['n'] if self.puzzle else 4
                    if pygame.K_1 <= k <= pygame.K_9:
                        num = k - pygame.K_0
                        if num <= n:
                            self.input_num(num)
                    elif k in (pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_0):
                        self.input_num(0)
                    elif self.sel and self.puzzle:
                        r,c = self.sel
                        if k == pygame.K_UP:    self.select_cell(max(0,r-1),c)
                        if k == pygame.K_DOWN:  self.select_cell(min(n-1,r+1),c)
                        if k == pygame.K_LEFT:  self.select_cell(r,max(0,c-1))
                        if k == pygame.K_RIGHT: self.select_cell(r,min(n-1,c+1))

            # draw
            self.draw_header()

            # top controls
            for dd in [self.dd_size, self.dd_diff]:
                dd.draw(self.screen, self.font_btn)
            self.btn_gen.draw(self.screen, self.font_btn)
            if self.puzzle:
                self.btn_check.draw(self.screen, self.font_btn)
                self.btn_solve.draw(self.screen, self.font_btn)

            self.draw_status()

            # separator line
            pygame.draw.line(self.screen, BORDER, (0,56), (self.screen.get_width(),56), 1)

            self.draw_grid()
            self.draw_numpad()
            self.draw_info()

            if self.won:
                self.draw_win()

            pygame.display.flip()
            self.clock.tick(60)


# ──────────────────────────────────────────────
if __name__ == '__main__':
    KenKen().run()
