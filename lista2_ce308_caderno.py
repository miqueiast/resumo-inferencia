#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lista 2 – CE308 Teoria da Probabilidade 2 (UFPR, 2026/2)
Resolução completa das 28 questões em folhas de caderno pautado "escritas à mão".

Requisitos:  pip install pillow pypdf
Entrada:     Lista2-CE308-TP2-2026-2.pdf (na pasta do script, na pasta atual
             ou passado como 1º argumento: python script.py caminho/da/lista.pdf)
Saída:       resolucao_página_1.png, resolucao_página_2.png, ...  (1500 x 2400 px)

Marcação usada nas linhas de resolução:
    ^{...} sobrescrito    _{...} subscrito    (ou ^x / _x para um só caractere)
    Um subscrito seguido de sobrescrito é empilhado (ex.: ∫_{0}^{∞}).
"""
from __future__ import annotations

import math
import random
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ════════════════════════════ CONFIGURAÇÃO ════════════════════════════
SEED = 2026                    # None → caligrafia diferente a cada execução
PDF_NAME = "Lista2-CE308-TP2-2026-2.pdf"
OUT_PREFIX = "resolucao_página"

PAGE_W, PAGE_H = 1500, 2400
LINE_GAP = 60                  # distância entre as pautas azuis
FIRST_RULE = 230               # y da primeira pauta
BOTTOM_PAD = 110
MARGIN_X = 175                 # margem vermelha
TEXT_X = MARGIN_X + 22
RIGHT_PAD = 70
INDENT = 48                    # recuo das equações
X_HEIGHT = 0.30 * LINE_GAP     # altura-x da letra (ajusta qualquer fonte à pauta)
HOLES = True                   # furos de fichário na borda esquerda

PAPER = (253, 252, 245)
RULE_BLUE = (170, 200, 230)
MARGIN_RED = (225, 95, 95)
INKS = {
    "preta": (25, 25, 30),
    "azul": (20, 50, 140),
    "vermelha": (190, 35, 35),
}

#           cor da caneta, escala da letra, nível de recuo, sublinhado, caixa
STYLES = {
    "titulo":    dict(ink="preta",    scale=1.25, indent=0, underline=True,  box=False),
    "enunciado": dict(ink="preta",    scale=1.00, indent=0, underline=False, box=False),
    "item":      dict(ink="preta",    scale=1.08, indent=0, underline=False, box=False),
    "texto":     dict(ink="azul",     scale=1.00, indent=0, underline=False, box=False),
    "eq":        dict(ink="azul",     scale=1.00, indent=1, underline=False, box=False),
    "res":       dict(ink="vermelha", scale=1.05, indent=1, underline=False, box=True),
    "chave":     dict(ink="vermelha", scale=1.00, indent=0, underline=False, box=False),
}

# ════════════════════════════ FONTES ════════════════════════════
try:
    BASE_DIR = Path(__file__).resolve().parent
except NameError:  # executando em notebook
    BASE_DIR = Path.cwd()
FONT_DIR = BASE_DIR / "fontes"

# Fontes manuscritas em ordem de preferência
HAND_FONTS_LOCAL = [
    "segoepr.ttf", "C:/Windows/Fonts/segoepr.ttf", "Segoe Print.ttf",
    str(FONT_DIR / "Caveat.ttf"), "Caveat-Regular.ttf",
    str(FONT_DIR / "IndieFlower.ttf"), "IndieFlower-Regular.ttf",
]
HAND_FONTS_LAST_RESORT = [
    "Comic Sans MS.ttf", "comic.ttf", "C:/Windows/Fonts/comic.ttf",
    "/Library/Fonts/Comic Sans MS.ttf",
    "/System/Library/Fonts/Supplemental/Comic Sans MS.ttf",
    "/usr/share/fonts/truetype/msttcorefonts/Comic_Sans_MS.ttf",
]
# Baixadas do repositório Google Fonts (licença OFL) se nada acima existir
FONT_URLS = {
    "Caveat.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/caveat/Caveat%5Bwght%5D.ttf",
    "IndieFlower.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/indieflower/IndieFlower-Regular.ttf",
}
# Fontes de reserva para símbolos que a manuscrita não tem (λ, ∫, ∞, √, Σ, ⇒ ...)
SYMBOL_FONTS = [
    "seguisym.ttf", "C:/Windows/Fonts/seguisym.ttf",
    "segoeui.ttf", "C:/Windows/Fonts/segoeui.ttf",
    "cambria.ttc", "C:/Windows/Fonts/cambria.ttc",
    "DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
    "arial.ttf", "Arial.ttf",
]
ASCII_SUBST = {"−": "-", "’": "'", "…": "...", "“": '"', "”": '"'}
BIG_OPS = {"∫": (1.75, 0.35), "Σ": (1.3, 0.12), "∏": (1.3, 0.12), "√": (1.25, 0.08)}
NBSP = "\u00a0"  # espaço que não quebra linha
_REF = 200       # tamanho de referência para medir a altura-x


def _load(path: str, size: int):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return None


def _matplotlib_dejavu() -> list[str]:
    try:
        import matplotlib
        return [str(Path(matplotlib.get_data_path()) / "fonts" / "ttf" / "DejaVuSans.ttf")]
    except Exception:
        return []


def _download_fonts() -> None:
    try:
        FONT_DIR.mkdir(exist_ok=True)
    except OSError:
        return
    for name, url in FONT_URLS.items():
        dest = FONT_DIR / name
        if dest.exists():
            continue
        try:
            urllib.request.urlretrieve(url, dest)
        except Exception:
            if dest.exists():
                dest.unlink()


def _glyph_signature(font, ch: str):
    l, t, r, b = font.getbbox(ch)
    w, h = max(1, r - l), max(1, b - t)
    im = Image.new("L", (w, h), 0)
    ImageDraw.Draw(im).text((-l, -t), ch, font=font, fill=255)
    return (w, h), im.tobytes()


class _DefaultBook:
    """Último recurso: ImageFont.load_default() quando não há nenhuma TrueType."""

    def __init__(self) -> None:
        try:
            self.base = ImageFont.load_default(size=int(LINE_GAP * 0.5))
        except TypeError:
            self.base = ImageFont.load_default()
        self.hand = self.symbols = None

    def font(self, path, xh):
        try:
            return ImageFont.load_default(size=max(8, int(xh * 2)))
        except TypeError:
            return self.base

    def pick(self, ch):
        return ASCII_SUBST.get(ch, ch), None


class FontBook:
    """Fonte manuscrita + cadeia de reservas, todas normalizadas pela altura-x."""

    def __init__(self) -> None:
        self.hand = self._find_hand()
        seen, self.symbols = set(), []
        for p in SYMBOL_FONTS + _matplotlib_dejavu():
            f = _load(p, 20)
            if f and p != self.hand and f.getname() not in seen:
                seen.add(f.getname())
                self.symbols.append(p)
        if self.hand is None and not self.symbols:
            raise LookupError("sem fontes TrueType")
        if self.hand is None:  # fonte comum no lugar da manuscrita
            self.hand = self.symbols.pop(0)
        self.chain = [self.hand] + self.symbols
        self._ratio: dict[str, float] = {}
        self._fonts: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}
        self._notdef: dict[str, tuple] = {}
        self._pick: dict[str, tuple[str, str]] = {}
        for p in self.chain:
            ref = _load(p, _REF)
            l, t, r, b = ref.getbbox("x", anchor="ls")
            self._ratio[p] = _REF / max(1, b - t)

    @staticmethod
    def _find_hand():
        for p in HAND_FONTS_LOCAL:
            if _load(p, 20):
                return p
        _download_fonts()
        for p in HAND_FONTS_LOCAL + HAND_FONTS_LAST_RESORT:
            if _load(p, 20):
                return p
        return None

    def font(self, path: str, xh: float):
        size = max(6, round(self._ratio[path] * xh))
        key = (path, size)
        if key not in self._fonts:
            self._fonts[key] = _load(path, size)
        return self._fonts[key]

    def _has(self, path: str, ch: str) -> bool:
        f = self.font(path, 60)
        if path not in self._notdef:
            self._notdef[path] = _glyph_signature(f, "\U0010FFFD")
        try:
            sig = _glyph_signature(f, ch)
        except Exception:
            return False
        return sig != self._notdef[path] and sig[1].strip(b"\x00") != b""

    def pick(self, ch: str) -> tuple[str, str]:
        """Retorna (caractere a desenhar, caminho da fonte que o possui)."""
        if ch not in self._pick:
            choice = (ch, self.chain[-1])
            if self._has(self.hand, ch):
                choice = (ch, self.hand)
            elif ch in ASCII_SUBST and self._has(self.hand, ASCII_SUBST[ch]):
                choice = (ASCII_SUBST[ch], self.hand)
            else:
                for p in self.symbols:
                    if self._has(p, ch):
                        choice = (ch, p)
                        break
            self._pick[ch] = choice
        return self._pick[ch]


def make_book():
    try:
        return FontBook()
    except LookupError:
        return _DefaultBook()


# ════════════════════════════ TEXTO COM ÍNDICES ════════════════════════════
NORMAL, SUP, SUB = 0, 1, 2


def parse(text: str) -> list[tuple[str, int, int]]:
    """Converte a marcação em tokens (caractere, modo, grupo)."""
    tokens, i, group = [], 0, 0
    while i < len(text):
        c = text[i]
        if c in "^_" and i + 1 < len(text):
            mode = SUP if c == "^" else SUB
            group += 1
            if text[i + 1] == "{":
                j = text.find("}", i + 2)
                j = len(text) if j == -1 else j
                tokens += [(ch, mode, group) for ch in text[i + 2:j]]
                i = j + 1
            else:
                tokens.append((text[i + 1], mode, group))
                i += 2
            continue
        tokens.append((c, NORMAL, 0))
        i += 1
    return tokens


def raw_tokens(text: str):
    """Texto literal (enunciados do PDF): sem interpretar ^ e _."""
    return [(c, NORMAL, 0) for c in text]


def layout(tokens, xh: float, book, rnd: random.Random | None = None):
    """Posiciona cada glifo; com rnd, aplica as imperfeições da escrita."""
    glyphs, x = [], 0.0
    cur_group, prev_mode, group_start = None, NORMAL, 0.0
    last_sub = None
    stack_end = None
    for ch, mode, g in tokens:
        if g != cur_group or mode != prev_mode:
            last_sub = (group_start, x) if prev_mode == SUB else None
            if mode == SUP and last_sub is not None:
                stack_end, x = last_sub[1], last_sub[0]
            elif stack_end is not None:
                x, stack_end = max(x, stack_end), None
            cur_group, prev_mode, group_start = g, mode, x
        scale = 1.0 if mode == NORMAL else 0.62
        dy = {NORMAL: 0.0, SUP: -1.05 * xh, SUB: 0.42 * xh}[mode]
        gxh = xh * scale
        if ch in (" ", NBSP):
            x += 0.95 * gxh + (rnd.uniform(-0.08, 0.15) * xh if rnd else 0)
            continue
        draw_ch, path = book.pick(ch)
        big, big_dy = BIG_OPS.get(ch, (1.0, 0.0))
        f = book.font(path, gxh * big)
        jy = rnd.uniform(-0.06, 0.06) * xh if rnd else 0.0
        glyphs.append((x, dy + big_dy * gxh + jy, draw_ch, f))
        x += f.getlength(draw_ch) + (rnd.uniform(-0.03, 0.07) * xh if rnd else 0.02 * xh)
    if stack_end is not None:
        x = max(x, stack_end)
    return glyphs, x


def wrap(tokens, xh, book, max_w, hang):
    """Quebra por palavras (espaços normais) respeitando a largura útil."""
    words, cur = [], []
    for t in tokens:
        if t[0] == " " and t[1] == NORMAL:
            words.append(cur)
            cur = []
        else:
            cur.append(t)
    words.append(cur)
    lines, line = [], None
    sp = [(" ", NORMAL, 0)]
    for w in words:
        trial = w if line is None else line + sp + w
        limit = max_w - (hang if lines else 0)
        if line is not None and line and layout(trial, xh, book)[1] > limit:
            lines.append(line)
            line = w
        else:
            line = trial
    lines.append(line or [])
    return lines


# ════════════════════════════ DESENHO ════════════════════════════
def vary(rgb, rnd, amount=10):
    return tuple(max(0, min(255, c + rnd.randint(-amount, amount))) for c in rgb)


def hand_line(draw, p0, p1, color, width, rnd, amp=1.6):
    """Traço levemente ondulado, como feito à mão."""
    (x0, y0), (x1, y1) = p0, p1
    dist = math.hypot(x1 - x0, y1 - y0)
    n = max(2, int(dist / 18))
    nx, ny = -(y1 - y0) / max(dist, 1), (x1 - x0) / max(dist, 1)
    phase, freq = rnd.uniform(0, 2 * math.pi), rnd.uniform(0.8, 1.6)
    pts = []
    for i in range(n + 1):
        t = i / n
        off = amp * math.sin(2 * math.pi * freq * t + phase) + rnd.uniform(-0.4, 0.4)
        pts.append((x0 + (x1 - x0) * t + nx * off, y0 + (y1 - y0) * t + ny * off))
    draw.line(pts, fill=color, width=width, joint="curve")


def draw_line_of_text(page, tokens, x0, baseline, xh, ink, book, rnd):
    glyphs, w = layout(tokens, xh, book, rnd)
    pad, h, base_in = int(2 * xh), int(LINE_GAP * 3), int(LINE_GAP * 1.8)
    layer = Image.new("RGBA", (int(w) + 2 * pad, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    pressure = rnd.uniform(0.9, 1.0)  # pressão da caneta varia por linha
    for gx, gy, ch, f in glyphs:
        alpha = int(rnd.randint(215, 252) * pressure)
        try:
            d.text((pad + gx, base_in + gy), ch, font=f, fill=vary(ink, rnd) + (alpha,), anchor="ls")
        except (ValueError, TypeError):  # fonte bitmap sem suporte a âncora
            d.text((pad + gx, base_in + gy - xh * 1.6), ch, font=f, fill=vary(ink, rnd) + (alpha,))
    angle = rnd.uniform(-0.3, 0.3)  # linha ligeiramente torta
    layer = layer.rotate(angle, resample=Image.BICUBIC, center=(pad, base_in))
    layer = layer.filter(ImageFilter.GaussianBlur(0.45))  # borda de tinta de esferográfica
    page.alpha_composite(layer, (int(x0 - pad), int(baseline - base_in)))
    return w


def blank_page(rules, rnd, book):
    page = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    noise = Image.effect_noise((PAGE_W, PAGE_H), 12).convert("RGB")
    page = Image.blend(page, noise, 0.02)  # fibra do papel
    d = ImageDraw.Draw(page)
    for y in rules:
        d.line([(0, y), (PAGE_W, y)], fill=RULE_BLUE, width=2)
    d.line([(MARGIN_X, 0), (MARGIN_X, PAGE_H)], fill=MARGIN_RED, width=3)
    d.line([(MARGIN_X + 6, 0), (MARGIN_X + 6, PAGE_H)], fill=MARGIN_RED, width=1)
    pf = book.font(book.symbols[0] if book.symbols else book.hand, 0.22 * LINE_GAP)
    d.text((PAGE_W - 500, FIRST_RULE - 1.7 * LINE_GAP), "Data: ____/____/______",
           font=pf, fill=(125, 155, 195))
    if HOLES:
        for y in range(150, PAGE_H - 100, 200):
            d.ellipse([38, y - 20, 78, y + 20], fill=(228, 226, 218), outline=(200, 197, 188), width=2)
    return page.convert("RGBA")


# ════════════════════════════ LEITURA DO PDF (pypdf) ════════════════════════════
ENUNCIADOS_RESERVA = {
    1: "X1, ..., Xn iid Pareto(1, c): f(x) = c/x^(c+1), x ≥ 1, c > 0. Encontre a distribuição de Y1 e Yn (mínimo e máximo).",
    2: "X1, ..., Xn independentes, Xi ~ exp(λi), Y = min Xi. Mostre que Y ~ exp(λ1 + ... + λn).",
    3: "Y1 e Yn: mínimo e máximo de a.a. de U(a, b). a) densidade conjunta para n = 3; b) n geral; c) U(0,1): cov(Y1, Yn) = 1/[(n+1)²(n+2)].",
    4: "Duas baterias iid exp(λ) em série. a) P(sistema > t); b) vida esperada; c) λ = 1/3.",
    5: "f(x, y) = 1/x, 0 ≤ y ≤ x ≤ 1. Calcule f(y|x). Reconhece essa distribuição?",
    6: "f(x, y) = λ² e^(−λy), 0 ≤ x ≤ y. Calcule f(y|x). Reconhece essa distribuição?",
    7: "(X, Y) ~ U(R), R = {0 < x < y < 1}. Distribuições condicionais de X/Y e Y/X.",
    8: "f(x, y) = 8xy, 0 < x < y < 1. Esperança e variância de X dado Y.",
    9: "X ~ U(0,1); dado X = x, Y ~ U(−x, x). a) conjunta; b) marginal de Y; c) condicional de X dado Y.",
    10: "pX(x) = x/3, x = 1, 2; p(y|x) = C(x,y)(1/2)^x, y ≤ x. Conjunta de X e Y e marginal de Y.",
    11: "X ~ N(0,1), Y ~ N(1,4) independentes. Distribuição de (X, Y) e de 2X dado Y = y.",
    12: "Passas ~ Poisson(60); cada passa vai para você com prob. 1/2. Distribuição e esperança do número de passas que você recebe.",
    13: "Y ~ Poisson(λ) e X | Y = n ~ Bin(n, p). a) distribuição de X; b) distribuição de Y dado X.",
    14: "X ~ Bin(m, p), Y ~ Bin(n, p) independentes. E(X | X + Y).",
    15: "X1, X2 iid geométricas P(Xi = n) = p(1 − p)^n, n = 0, 1, ... Distribuição de X1 dado X1 + X2.",
    16: "fX(x) = x/8, 0 < x < 4; Y | X = x ~ U(0, x). a) conjunta; b) marginal de Y.",
    17: "Nº de acidentes: média μ, variância σ². Feridos por acidente iid: média ξ, variância τ². Média e variância do total de feridos.",
    18: "X ~ U(0,1); dado X = x, Y ~ Bin(n, x). E(Y) e var(Y).",
    19: "X ~ N(μ, 1) e Y | X = x ~ N(x/2, σ²). a) distribuição de Z = E(Y|X); b) E(Y).",
    20: "Prove que X e Y − E(Y|X) são não correlacionadas.",
    21: "p(i, j) = (3 + 2i − j)/45, i, j ∈ {1, 2, 3}. a) E(X), E(Y); b) var; c) cov; d) ρ.",
    22: "f(x, y) = e^(−y) e^(−x/y) / y, x > 0, y > 0. a) E(X|Y); b) independência; c) EX = EY = 1; d) correlação.",
    23: "Demonstre que var(Y) = E[var(Y|X)] + var[E(Y|X)].",
    24: "a) Y ~ N(0,4), E(X|Y) = aY + b; a, b com E(X) = 1 e E(XY) = 2. b) Y ~ Bernoulli(p), E(X|Y=0) = 1, E(X|Y=1) = 2: E(X).",
    25: "f(x, y) = xy/2, 0 < x < y < 2. Covariância. São independentes?",
    26: "f(x, y) = e^(−3y)(2y)^x / x!, y > 0, x = 0, 1, ... a) X | Y = y; b) distribuição de X; c) E[E(X|Y)] = E(X).",
    27: "var(X + Y) = 0. Coeficiente de correlação entre X e Y.",
    28: "Demonstrar: cov(X, Y) = E[cov(X, Y | Z)] + cov[E(X|Z), E(Y|Z)].",
}


def localizar_pdf() -> Path | None:
    candidatos = []
    if len(sys.argv) > 1:
        candidatos.append(Path(sys.argv[1]))
    candidatos += [BASE_DIR / PDF_NAME, Path.cwd() / PDF_NAME,
                   Path("/mnt/user-data/uploads") / PDF_NAME]
    for c in candidatos:
        if c.is_file():
            return c
    return None


def extrair_enunciados() -> dict[int, str]:
    """Lê o PDF com pypdf e separa o texto das 28 questões."""
    enunciados = dict(ENUNCIADOS_RESERVA)
    caminho = localizar_pdf()
    if caminho is None:
        return enunciados
    try:
        from pypdf import PdfReader
        texto = "\n".join((pg.extract_text() or "") for pg in PdfReader(str(caminho)).pages)
    except Exception:
        return enunciados
    texto = unicodedata.normalize("NFKC", texto)      # 𝑋 → X, 𝜆 → λ ...
    texto = texto.replace("⁄", "/").replace("\u2215", "/")
    linhas = []
    for ln in texto.splitlines():
        s = ln.strip()
        letras = [c for c in s if c.isalpha()]
        if letras and all(c.isupper() for c in letras) and len(letras) > 8:
            continue                                      # cabeçalhos/seções em CAIXA ALTA
        linhas.append(s)
    texto = "\n".join(linhas)
    marcas, esperado = [], 1
    for m in re.finditer(r"(?m)^\s*(\d{1,2})\.\s", texto):
        if int(m.group(1)) == esperado:
            marcas.append((esperado, m.start(), m.end()))
            esperado += 1
    for k, (num, _, fim) in enumerate(marcas):
        prox = marcas[k + 1][1] if k + 1 < len(marcas) else len(texto)
        bruto = re.sub(r"\s+", " ", texto[fim:prox]).strip()
        bruto = re.sub(r"Prof\..*$", "", bruto).strip()
        if len(bruto) > 15:
            enunciados[num] = bruto
    return enunciados


# ════════════════════════════ RESOLUÇÕES ════════════════════════════
# (estilo, texto)  —  estilos: item (preta), texto/eq (azul), res/chave (vermelha), espaco
R: dict[int, list[tuple[str, str]]] = {}

R[1] = [
    ("texto", "Dados: f(x) = c/x^{c+1} = c·x^{−(c+1)},  x ≥ 1,  c > 0;  X_{1}, ..., X_{n} iid."),
    ("item", "Passo 1 – f.d.a. de cada X_{i}"),
    ("eq", "F(x) = ∫_{1}^{x} c·t^{−c−1} dt = c·[t^{−c}/(−c)]_{1}^{x}"),
    ("eq", "= (−x^{−c}) − (−1) = 1 − x^{−c},   x ≥ 1"),
    ("eq", "Logo:  P(X_{i} > x) = 1 − F(x) = x^{−c}"),
    ("item", "Passo 2 – Mínimo Y_{1} = min X_{i}"),
    ("texto", "O menor passa de y ⇔ todos passam de y:"),
    ("eq", "P(Y_{1} > y) = P(X_{1} > y, ..., X_{n} > y) = ∏ P(X_{i} > y)   (ind.)"),
    ("eq", "= [1 − F(y)]^{n}   (i.d.)   = (y^{−c})^{n} = y^{−nc}"),
    ("eq", "F_{Y₁}(y) = 1 − y^{−nc},   y ≥ 1"),
    ("eq", "f_{Y₁}(y) = d/dy [1 − y^{−nc}] = −(−nc)y^{−nc−1} = nc·y^{−nc−1}"),
    ("res", "f_{Y₁}(y) = nc / y^{nc+1},  y ≥ 1   ⇒   Y_{1} ~ Pareto(1, nc)"),
    ("item", "Passo 3 – Máximo Y_{n} = max X_{i}"),
    ("texto", "O maior fica abaixo de y ⇔ todos ficam abaixo de y:"),
    ("eq", "F_{Yₙ}(y) = P(X_{1} ≤ y, ..., X_{n} ≤ y) = [F(y)]^{n} = (1 − y^{−c})^{n}   (ind., i.d.)"),
    ("texto", "Derivando pela regra da cadeia:  d/dy (1 − y^{−c}) = c·y^{−c−1}"),
    ("eq", "f_{Yₙ}(y) = n(1 − y^{−c})^{n−1} · c·y^{−c−1}"),
    ("res", "f_{Yₙ}(y) = nc(1 − y^{−c})^{n−1} / y^{c+1},  y ≥ 1"),
    ("texto", "Checagem n = 1: as duas fórmulas voltam a c/y^{c+1}  ✓"),
]

R[2] = [
    ("texto", "Dados: X_{i} ~ exp(λ_{i}) independentes;  f(x) = λ_{i}e^{−λᵢx}, x > 0  (taxa λ_{i})."),
    ("texto", "Obs.: as taxas podem ser diferentes, então são independentes (não identicamente distr.)."),
    ("item", "Em separado: cauda da exponencial"),
    ("eq", "P(X_{i} > y) = ∫_{y}^{∞} λ_{i}e^{−λᵢx} dx = [−e^{−λᵢx}]_{y}^{∞} = 0 + e^{−λᵢy} = e^{−λᵢy}"),
    ("item", "Distribuição de Y = min X_{i}"),
    ("eq", "P(Y > y) = P(X_{1} > y, ..., X_{n} > y) = ∏_{i=1}^{n} P(X_{i} > y)   (ind.)"),
    ("eq", "= e^{−λ₁y}·e^{−λ₂y}···e^{−λₙy} = e^{−(λ₁+···+λₙ)y},   y > 0"),
    ("eq", "F_{Y}(y) = 1 − e^{−(λ₁+···+λₙ)y}   ⇒   f_{Y}(y) = (λ_{1}+···+λ_{n})e^{−(λ₁+···+λₙ)y}"),
    ("texto", "Essa é exatamente a f.d.p. de uma exponencial de taxa Λ = λ_{1} + ··· + λ_{n}."),
    ("res", "Y = min X_{i} ~ exp(λ_{1} + ··· + λ_{n})   ∎"),
]

R[3] = [
    ("texto", "Dados: X_{i} ~ U(a, b):  f(x) = 1/(b−a),  F(x) = (x−a)/(b−a),  a < x < b."),
    ("item", "Ideia: f.d.a. conjunta de (Y_{1}, Y_{n}) para u < v"),
    ("eq", "P(Y_{1} > u, Y_{n} ≤ v) = P(todos os X_{i} em (u, v]) = [F(v) − F(u)]^{n}   (ind., i.d.)"),
    ("eq", "F(u, v) = P(Y_{1} ≤ u, Y_{n} ≤ v) = P(Y_{n} ≤ v) − P(Y_{1} > u, Y_{n} ≤ v)"),
    ("eq", "F(u, v) = [F(v)]^{n} − [F(v) − F(u)]^{n}"),
    ("texto", "A densidade conjunta é f(u, v) = ∂²F/∂u∂v."),
    ("eq", "∂F/∂v = n[F(v)]^{n−1}f(v) − n[F(v) − F(u)]^{n−1}f(v)"),
    ("eq", "∂²F/∂u∂v = 0 − n(n−1)[F(v) − F(u)]^{n−2}·(−f(u))·f(v)"),
    ("chave", "f_{Y₁,Yₙ}(u, v) = n(n−1)[F(v) − F(u)]^{n−2} f(u) f(v),   u < v"),
    ("item", "a) n = 3"),
    ("texto", "Substituindo F(v) − F(u) = (v − u)/(b − a) e f(u) = f(v) = 1/(b − a):"),
    ("eq", "f(y_{1}, y_{n}) = 3·2·[(y_{n} − y_{1})/(b − a)]^{1} · 1/(b − a) · 1/(b − a)"),
    ("res", "f(y_{1}, y_{n}) = 6(y_{n} − y_{1})/(b − a)^{3},   a < y_{1} < y_{n} < b   ✓"),
    ("item", "b) n geral"),
    ("eq", "f(y_{1}, y_{n}) = n(n−1)·(y_{n} − y_{1})^{n−2}/(b − a)^{n−2} · 1/(b − a)^{2}"),
    ("res", "f(y_{1}, y_{n}) = n(n−1)(y_{n} − y_{1})^{n−2}/(b − a)^{n},   a < y_{1} < y_{n} < b"),
    ("item", "c) U(0, 1):  f(y_{1}, y_{n}) = n(n−1)(y_{n} − y_{1})^{n−2},  0 < y_{1} < y_{n} < 1"),
    ("texto", "Marginais (mesma ideia de Q1):  f_{Y₁}(y) = n(1−y)^{n−1}  e  f_{Yₙ}(y) = n·y^{n−1}."),
    ("texto", "Em separado:"),
    ("eq", "E(Y_{n}) = ∫_{0}^{1} y·n·y^{n−1} dy = n∫_{0}^{1} y^{n} dy = n/(n+1)"),
    ("eq", "E(Y_{1}) = ∫_{0}^{1} y·n(1−y)^{n−1} dy;   subst. w = 1 − y  (dw = −dy):"),
    ("eq", "= n∫_{0}^{1} (1 − w)w^{n−1} dw = n[1/n − 1/(n+1)] = 1 − n/(n+1) = 1/(n+1)"),
    ("eq", "E(Y_{1}Y_{n}) = ∫_{0}^{1} ∫_{0}^{v} u·v·n(n−1)(v − u)^{n−2} du dv"),
    ("texto", "Integral de dentro (v fixo), subst. w = v − u  ⇒  u = v − w, du = −dw:"),
    ("eq", "∫_{0}^{v} u(v − u)^{n−2} du = ∫_{0}^{v} (v − w)w^{n−2} dw = v·v^{n−1}/(n−1) − v^{n}/n"),
    ("eq", "= v^{n}[1/(n−1) − 1/n] = v^{n}/[n(n−1)]"),
    ("eq", "E(Y_{1}Y_{n}) = ∫_{0}^{1} v·n(n−1)·v^{n}/[n(n−1)] dv = ∫_{0}^{1} v^{n+1} dv = 1/(n+2)"),
    ("eq", "cov(Y_{1}, Y_{n}) = E(Y_{1}Y_{n}) − E(Y_{1})E(Y_{n}) = 1/(n+2) − n/(n+1)^{2}"),
    ("eq", "= [(n+1)^{2} − n(n+2)] / [(n+1)^{2}(n+2)] = [n² + 2n + 1 − n² − 2n] / [(n+1)^{2}(n+2)]"),
    ("res", "cov(Y_{1}, Y_{n}) = 1 / [(n+1)^{2}(n+2)]   ✓"),
]

R[4] = [
    ("texto", "Dados: X_{1}, X_{2} iid exp(λ);  em série ⇒ o sistema dura T = min(X_{1}, X_{2})."),
    ("item", "a) P(T > t)"),
    ("eq", "P(T > t) = P(X_{1} > t)·P(X_{2} > t)   (ind.)   = e^{−λt}·e^{−λt}"),
    ("res", "P(T > t) = e^{−2λt},  t > 0   ⇒   T ~ exp(2λ)   (caso n = 2 da Q2)"),
    ("item", "b) E(T)"),
    ("eq", "E(T) = ∫_{0}^{∞} P(T > t) dt = ∫_{0}^{∞} e^{−2λt} dt = [−e^{−2λt}/(2λ)]_{0}^{∞} = 1/(2λ)"),
    ("texto", "(Para v.a. ≥ 0: E(T) = ∫_{0}^{∞} P(T > t) dt; ou direto: média da exp(2λ) é 1/(2λ).)"),
    ("res", "E(T) = 1/(2λ) horas"),
    ("item", "c) λ = 1/3"),
    ("eq", "2λ = 2/3   ⇒   P(T > t) = e^{−2t/3}"),
    ("eq", "E(T) = 1/(2·1/3) = 3/2"),
    ("res", "P(T > t) = e^{−2t/3}   e   E(T) = 1,5 hora"),
]

R[5] = [
    ("texto", "Dados: f(x, y) = 1/x,  0 ≤ y ≤ x ≤ 1."),
    ("item", "Marginal de X  (x fixo, y vai de 0 a x)"),
    ("eq", "f_{X}(x) = ∫_{0}^{x} (1/x) dy = (1/x)·[y]_{0}^{x} = (1/x)·x = 1,   0 < x ≤ 1   ⇒  X ~ U(0, 1)"),
    ("item", "Condicional"),
    ("eq", "f(y | x) = f(x, y)/f_{X}(x) = (1/x)/1 = 1/x,   0 ≤ y ≤ x"),
    ("res", "f(y | x) = 1/x, 0 ≤ y ≤ x   ⇒   Y | X = x ~ U(0, x)"),
    ("texto", "Sim: é a uniforme no intervalo (0, x) (densidade constante = 1/comprimento)."),
]

R[6] = [
    ("texto", "Dados: f(x, y) = λ²e^{−λy},  0 ≤ x ≤ y."),
    ("item", "Marginal de X  (x fixo, y vai de x a ∞)"),
    ("eq", "f_{X}(x) = ∫_{x}^{∞} λ²e^{−λy} dy = λ²[−e^{−λy}/λ]_{x}^{∞} = λ²·e^{−λx}/λ = λe^{−λx},  x ≥ 0"),
    ("texto", "Logo X ~ exp(λ)."),
    ("item", "Condicional"),
    ("eq", "f(y | x) = λ²e^{−λy} / (λe^{−λx}) = λe^{−λ(y − x)},   y ≥ x"),
    ("res", "f(y | x) = λe^{−λ(y−x)}, y ≥ x   ⇒   Y − x | X = x ~ exp(λ)"),
    ("texto", "É uma exponencial de taxa λ deslocada para começar em x (falta de memória)."),
]

R[7] = [
    ("texto", "Dados: (X, Y) uniforme no triângulo R = {0 < x < y < 1}."),
    ("eq", "Área(R) = (1·1)/2 = 1/2   ⇒   f(x, y) = 1/Área = 2,   0 < x < y < 1"),
    ("item", "Marginais"),
    ("eq", "f_{Y}(y) = ∫_{0}^{y} 2 dx = 2y,   0 < y < 1"),
    ("eq", "f_{X}(x) = ∫_{x}^{1} 2 dy = 2(1 − x),   0 < x < 1"),
    ("item", "X dado Y = y"),
    ("eq", "f(x | y) = 2/(2y) = 1/y,   0 < x < y"),
    ("res", "X | Y = y ~ U(0, y)"),
    ("item", "Y dado X = x"),
    ("eq", "f(y | x) = 2/[2(1 − x)] = 1/(1 − x),   x < y < 1"),
    ("res", "Y | X = x ~ U(x, 1)"),
]

R[8] = [
    ("texto", "Dados: f(x, y) = 8xy,  0 < x < y < 1."),
    ("eq", "f_{Y}(y) = ∫_{0}^{y} 8xy dx = 8y·[x²/2]_{0}^{y} = 8y·y²/2 = 4y³,   0 < y < 1"),
    ("eq", "f(x | y) = 8xy/(4y³) = 2x/y²,   0 < x < y"),
    ("texto", "Conferindo: ∫_{0}^{y} 2x/y² dx = (1/y²)·y² = 1  ✓"),
    ("item", "Esperança condicional"),
    ("eq", "E(X | Y = y) = ∫_{0}^{y} x·2x/y² dx = (2/y²)·[x³/3]_{0}^{y} = (2/y²)(y³/3) = 2y/3"),
    ("res", "E(X | Y) = 2Y/3"),
    ("item", "Variância condicional"),
    ("eq", "E(X² | Y = y) = ∫_{0}^{y} x²·2x/y² dx = (2/y²)·y⁴/4 = y²/2"),
    ("eq", "var(X | Y = y) = E(X² | y) − E^{2}(X | y) = y²/2 − 4y²/9 = (9y² − 8y²)/18"),
    ("res", "var(X | Y) = Y²/18"),
]

R[9] = [
    ("texto", "Dados: X ~ U(0, 1): f_{X}(x) = 1;   Y | X = x ~ U(−x, x): f(y | x) = 1/(2x), −x < y < x."),
    ("item", "a) Conjunta = marginal × condicional"),
    ("eq", "f(x, y) = f_{X}(x)·f(y | x) = 1·1/(2x)"),
    ("res", "f(x, y) = 1/(2x),   0 < x < 1,  −x < y < x   (ou seja |y| < x < 1)"),
    ("item", "b) Marginal de Y  (y fixo: x vai de |y| até 1)"),
    ("eq", "f_{Y}(y) = ∫_{|y|}^{1} 1/(2x) dx = (1/2)[ln x]_{|y|}^{1} = (1/2)(0 − ln|y|)"),
    ("res", "f_{Y}(y) = −(1/2)·ln|y|,   −1 < y < 1  (y ≠ 0)"),
    ("texto", "Conferindo: ∫_{−1}^{1} −(1/2)ln|y| dy = −∫_{0}^{1} ln y dy = −[y ln y − y]_{0}^{1} = 1  ✓"),
    ("item", "c) X dado Y = y"),
    ("eq", "f(x | y) = f(x, y)/f_{Y}(y) = [1/(2x)] / [−(1/2)ln|y|]"),
    ("res", "f(x | y) = −1/(x·ln|y|) = 1/[x·ln(1/|y|)],   |y| < x < 1"),
]

R[10] = [
    ("texto", "Dados: p_{X}(x) = x/3, x = 1, 2;   p(y | x) = C(x, y)(1/2)^{x}, y = 0, ..., x  (Bin(x, 1/2))."),
    ("texto", "Obs.: y começa em 0 — só assim Σ_{y} p(y | x) = (1/2 + 1/2)^{x} = 1."),
    ("eq", "p(x, y) = p_{X}(x)·p(y | x) = (x/3)·C(x, y)·(1/2)^{x}"),
    ("item", "x = 1:  (1/3)(1/2)C(1, y) = (1/6)C(1, y)"),
    ("eq", "p(1, 0) = 1/6,   p(1, 1) = 1/6"),
    ("item", "x = 2:  (2/3)(1/4)C(2, y) = (1/6)C(2, y)"),
    ("eq", "p(2, 0) = 1/6,   p(2, 1) = 2/6 = 1/3,   p(2, 2) = 1/6"),
    ("res", "Conjunta: p(1,0) = p(1,1) = p(2,0) = p(2,2) = 1/6;   p(2,1) = 1/3"),
    ("texto", "Soma: 1/6 + 1/6 + 1/6 + 2/6 + 1/6 = 1  ✓"),
    ("item", "Marginal de Y  (somar em x)"),
    ("eq", "P(Y = 0) = 1/6 + 1/6 = 1/3;   P(Y = 1) = 1/6 + 2/6 = 1/2;   P(Y = 2) = 0 + 1/6 = 1/6"),
    ("res", "p_{Y}(0) = 1/3,  p_{Y}(1) = 1/2,  p_{Y}(2) = 1/6"),
]

R[11] = [
    ("texto", "Dados: X ~ N(0, 1), Y ~ N(1, 4) independentes."),
    ("eq", "f(x, y) = f_{X}(x)f_{Y}(y)   (ind.)   = [1/√(2π)]e^{−x²/2} · [1/(2√(2π))]e^{−(y−1)²/8}"),
    ("eq", "f(x, y) = [1/(4π)]·exp{ −(1/2)[ x² + (y − 1)²/4 ] },   (x, y) ∈ ℝ²"),
    ("res", "(X, Y) ~ N_{2}( μ = (0, 1),  Σ = [[1, 0], [0, 4]] ),  ρ = 0"),
    ("item", "2X dado Y = y"),
    ("texto", "Como X e Y são independentes, saber Y = y não muda a distribuição de X:"),
    ("eq", "X | Y = y ~ N(0, 1)  ⇒  2X | Y = y ~ N(2·0, 2²·1)"),
    ("res", "2X | Y = y ~ N(0, 4)   (não depende de y)"),
]

R[12] = [
    ("texto", "Dados: N = nº de passas ~ Poisson(60);  dado N = n, cada passa é sua com prob. 1/2,"),
    ("texto", "de forma independente  ⇒  Y | N = n ~ Bin(n, 1/2)."),
    ("eq", "P(Y = k) = Σ_{n=k}^{∞} P(N = n)P(Y = k | N = n)   (prob. total)"),
    ("eq", "= Σ_{n=k}^{∞} [e^{−60}60^{n}/n!] · [n!/(k!(n−k)!)]·(1/2)^{n}"),
    ("texto", "Cancela n! e usa 60^{n}(1/2)^{n} = 30^{n} = 30^{k}·30^{n−k}:"),
    ("eq", "= [e^{−60}30^{k}/k!] · Σ_{n=k}^{∞} 30^{n−k}/(n−k)!   (subst. m = n − k)"),
    ("eq", "= [e^{−60}30^{k}/k!] · Σ_{m=0}^{∞} 30^{m}/m! = [e^{−60}30^{k}/k!]·e^{30}"),
    ("res", "P(Y = k) = e^{−30}30^{k}/k!,  k = 0, 1, ...   ⇒   Y ~ Poisson(30)"),
    ("eq", "E(Y) = E[E(Y | N)] = E(N/2) = 60/2"),
    ("res", "E(Y) = 30 passas"),
]

R[13] = [
    ("texto", "Dados: Y ~ Poisson(λ);  X | Y = n ~ Bin(n, p);  q = 1 − p."),
    ("item", "a) Distribuição de X"),
    ("eq", "P(X = k) = Σ_{n=k}^{∞} [e^{−λ}λ^{n}/n!]·[n!/(k!(n−k)!)]p^{k}q^{n−k}"),
    ("eq", "= [e^{−λ}(λp)^{k}/k!] · Σ_{n=k}^{∞} (λq)^{n−k}/(n−k)!   (λ^{n} = λ^{k}λ^{n−k})"),
    ("eq", "= [e^{−λ}(λp)^{k}/k!]·e^{λq} = e^{−λ(1−q)}(λp)^{k}/k!"),
    ("res", "P(X = k) = e^{−λp}(λp)^{k}/k!,  k = 0, 1, ...   ⇒   X ~ Poisson(λp)"),
    ("item", "b) Y dado X = k  (Bayes)"),
    ("eq", "P(Y = n | X = k) = P(Y = n)P(X = k | Y = n) / P(X = k),   n ≥ k"),
    ("eq", "= [e^{−λ}λ^{n}/n! · n!/(k!(n−k)!) p^{k}q^{n−k}] / [e^{−λp}(λp)^{k}/k!]"),
    ("texto", "Cancela k!, p^{k} e λ^{k};  e^{−λ}/e^{−λp} = e^{−λq}:"),
    ("eq", "= e^{−λq}λ^{n−k}q^{n−k}/(n−k)!"),
    ("res", "P(Y = n | X = k) = e^{−λq}(λq)^{n−k}/(n−k)!,  n = k, k+1, ..."),
    ("texto", "Ou seja: Y − k | X = k ~ Poisson(λ(1 − p))."),
]

R[14] = [
    ("texto", "Dados: X ~ Bin(m, p), Y ~ Bin(n, p) independentes ⇒ S = X + Y ~ Bin(m + n, p)."),
    ("eq", "P(X = k | S = s) = P(X = k, Y = s − k)/P(S = s) = P(X = k)P(Y = s − k)/P(S = s)   (ind.)"),
    ("eq", "= C(m,k)p^{k}q^{m−k}·C(n,s−k)p^{s−k}q^{n−s+k} / [C(m+n,s)p^{s}q^{m+n−s}]"),
    ("eq", "= C(m, k)C(n, s − k)/C(m + n, s)   (as potências de p e q cancelam)"),
    ("texto", "⇒ X | S = s ~ Hipergeométrica(m + n, m, s)."),
    ("item", "Em separado: média  (k·C(m,k) = m·C(m−1,k−1) e Vandermonde)"),
    ("eq", "Σ_{k} k·C(m,k)C(n,s−k) = m·Σ_{k} C(m−1,k−1)C(n,s−k) = m·C(m+n−1, s−1)"),
    ("eq", "E(X | S = s) = m·C(m+n−1, s−1)/C(m+n, s) = m·s/(m+n)   (pois C(N−1, s−1)/C(N, s) = s/N)"),
    ("res", "E(X | X + Y) = m(X + Y)/(m + n)"),
]

R[15] = [
    ("texto", "Dados: P(X_{i} = n) = pq^{n},  n = 0, 1, 2, ...;  q = 1 − p;  S = X_{1} + X_{2}."),
    ("item", "Em separado: distribuição de S"),
    ("eq", "P(S = s) = Σ_{k=0}^{s} P(X_{1} = k)P(X_{2} = s − k) = Σ_{k=0}^{s} pq^{k}·pq^{s−k}   (ind.)"),
    ("eq", "= Σ_{k=0}^{s} p²q^{s} = (s + 1)p²q^{s}"),
    ("item", "Condicional"),
    ("eq", "P(X_{1} = k | S = s) = pq^{k}·pq^{s−k} / [(s + 1)p²q^{s}] = p²q^{s}/[(s + 1)p²q^{s}]"),
    ("res", "P(X_{1} = k | X_{1} + X_{2} = s) = 1/(s + 1),  k = 0, 1, ..., s"),
    ("texto", "Uniforme discreta em {0, 1, ..., s}: não depende de p."),
]

R[16] = [
    ("texto", "Dados: f_{X}(x) = x/8, 0 < x < 4;   Y | X = x ~ U(0, x): f(y | x) = 1/x, 0 < y < x."),
    ("item", "a) Conjunta"),
    ("eq", "f(x, y) = f_{X}(x)·f(y | x) = (x/8)·(1/x)"),
    ("res", "f(x, y) = 1/8,   0 < y < x < 4"),
    ("item", "b) Marginal de Y  (y fixo, x vai de y a 4)"),
    ("eq", "f_{Y}(y) = ∫_{y}^{4} (1/8) dx = (4 − y)/8"),
    ("res", "f_{Y}(y) = (4 − y)/8,   0 < y < 4"),
    ("texto", "Conferindo: ∫_{0}^{4} (4 − y)/8 dy = (16 − 8)/8 = 1  ✓"),
]

R[17] = [
    ("texto", "Dados: N = nº de acidentes, E(N) = μ, var(N) = σ²;  X_{i} = feridos no acidente i, iid,"),
    ("texto", "E(X_{i}) = ξ, var(X_{i}) = τ², independentes de N.   Total: T = X_{1} + ··· + X_{N}."),
    ("item", "Condicionando em N = n  (soma de n parcelas iid)"),
    ("eq", "E(T | N = n) = nξ   (lin.)        var(T | N = n) = nτ²   (ind.)"),
    ("eq", "⇒  E(T | N) = Nξ   e   var(T | N) = Nτ²"),
    ("item", "Média  (esperança total)"),
    ("eq", "E(T) = E[E(T | N)] = E(Nξ) = ξE(N)"),
    ("res", "E(T) = μξ"),
    ("item", "Variância  (variância total — ver Q23)"),
    ("eq", "var(T) = E[var(T | N)] + var[E(T | N)] = E(Nτ²) + var(Nξ)"),
    ("eq", "= τ²E(N) + ξ²var(N)"),
    ("res", "var(T) = μτ² + ξ²σ²"),
]

R[18] = [
    ("texto", "Dados: X ~ U(0, 1);  Y | X = x ~ Bin(n, x)."),
    ("eq", "E(Y | X) = nX,     var(Y | X) = nX(1 − X)"),
    ("texto", "Em separado: E(X) = 1/2,  E(X²) = ∫_{0}^{1} x² dx = 1/3,  var(X) = 1/3 − 1/4 = 1/12."),
    ("item", "Esperança"),
    ("eq", "E(Y) = E[E(Y | X)] = nE(X) = n/2"),
    ("res", "E(Y) = n/2"),
    ("item", "Variância"),
    ("eq", "E[var(Y | X)] = n[E(X) − E(X²)] = n(1/2 − 1/3) = n/6"),
    ("eq", "var[E(Y | X)] = var(nX) = n²·1/12 = n²/12"),
    ("eq", "var(Y) = n/6 + n²/12 = (2n + n²)/12"),
    ("res", "var(Y) = n(n + 2)/12"),
    ("texto", "Curiosidade: Y é uniforme em {0, ..., n} e de fato var = [(n+1)² − 1]/12  ✓"),
]

R[19] = [
    ("texto", "Dados: X ~ N(μ, 1);  Y | X = x ~ N(x/2, σ²)  ⇒  E(Y | X = x) = x/2."),
    ("item", "a) Z = E(Y | X) = X/2"),
    ("texto", "Transformação linear de normal é normal: E(X/2) = μ/2,  var(X/2) = (1/4)·1."),
    ("res", "Z = X/2 ~ N(μ/2, 1/4)"),
    ("item", "b) E(Y)"),
    ("eq", "E(Y) = E[E(Y | X)] = E(X/2) = μ/2"),
    ("res", "E(Y) = μ/2"),
]

R[20] = [
    ("texto", "Supomos E|XY| < ∞ (para a covariância existir). Seja W = Y − E(Y | X)."),
    ("item", "Passo 1 – E(W) = 0"),
    ("eq", "E(W) = E(Y) − E[E(Y | X)] = E(Y) − E(Y) = 0   (esperança total)"),
    ("item", "Passo 2 – E(XW) = 0"),
    ("eq", "E(XW) = E(XY) − E[X·E(Y | X)]"),
    ("texto", "Em separado: X é \"constante\" dado X, então X·E(Y | X) = E(XY | X). Logo"),
    ("eq", "E[X·E(Y | X)] = E[E(XY | X)] = E(XY)"),
    ("eq", "⇒ E(XW) = E(XY) − E(XY) = 0"),
    ("item", "Conclusão"),
    ("eq", "cov(X, W) = E(XW) − E(X)E(W) = 0 − E(X)·0 = 0"),
    ("res", "cov(X, Y − E(Y | X)) = 0  ⇒  não correlacionadas   ∎"),
]

R[21] = [
    ("texto", "Dados: p(i, j) = (3 + 2i − j)/45;  X = i (linha), Y = j (coluna). Numeradores:"),
    ("eq", "i = 1:  4, 3, 2  (soma 9)     i = 2:  6, 5, 4  (soma 15)     i = 3:  8, 7, 6  (soma 21)"),
    ("eq", "Colunas: j = 1: 4+6+8 = 18;   j = 2: 3+5+7 = 15;   j = 3: 2+4+6 = 12.   Total 45  ✓"),
    ("eq", "p_{X}: 9/45, 15/45, 21/45          p_{Y}: 18/45, 15/45, 12/45"),
    ("item", "a) Esperanças"),
    ("eq", "E(X) = (1·9 + 2·15 + 3·21)/45 = (9 + 30 + 63)/45 = 102/45"),
    ("res", "E(X) = 34/15 ≈ 2,267"),
    ("eq", "E(Y) = (1·18 + 2·15 + 3·12)/45 = (18 + 30 + 36)/45 = 84/45"),
    ("res", "E(Y) = 28/15 ≈ 1,867"),
    ("item", "b) Variâncias"),
    ("eq", "E(X²) = (1·9 + 4·15 + 9·21)/45 = 258/45 = 86/15"),
    ("eq", "var(X) = 86/15 − (34/15)² = 1290/225 − 1156/225"),
    ("res", "var(X) = 134/225 ≈ 0,596"),
    ("eq", "E(Y²) = (1·18 + 4·15 + 9·12)/45 = 186/45 = 62/15"),
    ("eq", "var(Y) = 62/15 − (28/15)² = 930/225 − 784/225"),
    ("res", "var(Y) = 146/225 ≈ 0,649"),
    ("item", "c) Covariância"),
    ("eq", "E(XY) = Σ i·j·p(i, j):   i = 1: 1·(1·4 + 2·3 + 3·2) = 16"),
    ("eq", "i = 2: 2·(1·6 + 2·5 + 3·4) = 2·28 = 56;    i = 3: 3·(1·8 + 2·7 + 3·6) = 3·40 = 120"),
    ("eq", "E(XY) = (16 + 56 + 120)/45 = 192/45 = 64/15"),
    ("eq", "cov(X, Y) = 64/15 − (34/15)(28/15) = 960/225 − 952/225"),
    ("res", "cov(X, Y) = 8/225 ≈ 0,0356"),
    ("item", "d) Correlação"),
    ("eq", "ρ = cov/√(var X · var Y) = (8/225)/√(134·146/225²) = 8/√19564 = 8/139,87"),
    ("res", "ρ_{X,Y} ≈ 0,057"),
]

R[22] = [
    ("texto", "Dados: f(x, y) = e^{−y}e^{−x/y}/y,  x > 0, y > 0."),
    ("item", "Marginal de Y"),
    ("eq", "f_{Y}(y) = e^{−y}∫_{0}^{∞} (1/y)e^{−x/y} dx = e^{−y}·[−e^{−x/y}]_{0}^{∞} = e^{−y}·1"),
    ("texto", "⇒ Y ~ exp(1)."),
    ("item", "a) E(X | Y)"),
    ("eq", "f(x | y) = f(x, y)/f_{Y}(y) = (1/y)e^{−x/y},  x > 0   ⇒  X | Y = y ~ exp(taxa 1/y)"),
    ("eq", "E(X | Y = y) = 1/(taxa) = 1/(1/y) = y"),
    ("res", "E(X | Y) = Y"),
    ("item", "b) Independência"),
    ("texto", "f(x | y) = (1/y)e^{−x/y} depende de y, logo f(x | y) ≠ f_{X}(x)."),
    ("res", "X e Y não são independentes"),
    ("item", "c) E(X) = E(Y) = 1"),
    ("eq", "E(Y) = 1   (média da exp(1))"),
    ("eq", "E(X) = E[E(X | Y)] = E(Y) = 1"),
    ("res", "E(X) = E(Y) = 1   ✓"),
    ("item", "d) Correlação"),
    ("eq", "E(XY) = E[E(XY | Y)] = E[Y·E(X | Y)] = E(Y²)"),
    ("eq", "E(Y²) = var(Y) + E^{2}(Y) = 1 + 1 = 2"),
    ("eq", "cov(X, Y) = E(XY) − E(X)E(Y) = 2 − 1·1 = 1 ≠ 0"),
    ("res", "cov(X, Y) = 1  ⇒  X e Y são correlacionadas"),
]

R[23] = [
    ("texto", "Supomos E(Y²) < ∞ para que var(Y) exista. Definição condicional:"),
    ("eq", "var(Y | X) = E(Y² | X) − [E(Y | X)]²"),
    ("item", "Termo 1"),
    ("eq", "E[var(Y | X)] = E[E(Y² | X)] − E{[E(Y | X)]²} = E(Y²) − E{[E(Y | X)]²}   (esp. total)"),
    ("item", "Termo 2"),
    ("eq", "var[E(Y | X)] = E{[E(Y | X)]²} − {E[E(Y | X)]}² = E{[E(Y | X)]²} − E^{2}(Y)"),
    ("item", "Somando  (o termo E{[E(Y | X)]²} cancela)"),
    ("eq", "E[var(Y | X)] + var[E(Y | X)] = E(Y²) − E^{2}(Y) = var(Y)"),
    ("res", "var(Y) = E[var(Y | X)] + var[E(Y | X)]   ∎"),
]

R[24] = [
    ("item", "a) Y ~ N(0, 4): E(Y) = 0, E(Y²) = var(Y) + E^{2}(Y) = 4"),
    ("eq", "E(X) = E[E(X | Y)] = E(aY + b) = a·0 + b = b"),
    ("eq", "E(X) = 1  ⇒  b = 1"),
    ("eq", "E(XY) = E[Y·E(X | Y)] = E(aY² + bY) = a·4 + b·0 = 4a"),
    ("eq", "E(XY) = 2  ⇒  4a = 2  ⇒  a = 1/2"),
    ("res", "a = 1/2   e   b = 1"),
    ("item", "b) Y ~ Bernoulli(p)"),
    ("eq", "E(X) = E[E(X | Y)] = E(X | Y = 0)P(Y = 0) + E(X | Y = 1)P(Y = 1)"),
    ("eq", "= 1·(1 − p) + 2·p"),
    ("res", "E(X) = 1 + p"),
]

R[25] = [
    ("texto", "Dados: f(x, y) = xy/2,  0 < x < y < 2."),
    ("item", "Marginais"),
    ("eq", "f_{Y}(y) = ∫_{0}^{y} xy/2 dx = (y/2)(y²/2) = y³/4,   0 < y < 2"),
    ("eq", "f_{X}(x) = ∫_{x}^{2} xy/2 dy = (x/2)[y²/2]_{x}^{2} = (x/2)(4 − x²)/2 = x(4 − x²)/4,   0 < x < 2"),
    ("item", "Momentos"),
    ("eq", "E(X) = ∫_{0}^{2} x·x(4 − x²)/4 dx = (1/4)[4x³/3 − x⁵/5]_{0}^{2} = (1/4)(32/3 − 32/5) = (1/4)(64/15) = 16/15"),
    ("eq", "E(Y) = ∫_{0}^{2} y·y³/4 dy = (1/4)[y⁵/5]_{0}^{2} = (1/4)(32/5) = 8/5"),
    ("eq", "E(XY) = ∫_{0}^{2} ∫_{0}^{y} xy·xy/2 dx dy = (1/2)∫_{0}^{2} y²·(y³/3) dy = (1/6)[y⁶/6]_{0}^{2} = 64/36 = 16/9"),
    ("item", "Covariância"),
    ("eq", "cov(X, Y) = 16/9 − (16/15)(8/5) = 16/9 − 128/75 = (400 − 384)/225"),
    ("res", "cov(X, Y) = 16/225 ≈ 0,071"),
    ("item", "Independência"),
    ("texto", "cov ≠ 0 (e o suporte 0 < x < y < 2 não é um retângulo), logo f(x, y) ≠ f_{X}(x)f_{Y}(y)."),
    ("res", "X e Y não são independentes"),
]

R[26] = [
    ("texto", "Dados: f(x, y) = e^{−3y}(2y)^{x}/x!,  y > 0,  x = 0, 1, 2, ..."),
    ("item", "Marginal de Y  (somar em x; série de e^{t})"),
    ("eq", "f_{Y}(y) = e^{−3y} Σ_{x=0}^{∞} (2y)^{x}/x! = e^{−3y}·e^{2y} = e^{−y},  y > 0   ⇒  Y ~ exp(1)"),
    ("item", "a) X dado Y = y"),
    ("eq", "p(x | y) = f(x, y)/f_{Y}(y) = e^{−3y}(2y)^{x}/x! / e^{−y} = e^{−2y}(2y)^{x}/x!"),
    ("res", "X | Y = y ~ Poisson(2y)"),
    ("item", "b) Distribuição de X  (integrar em y)"),
    ("eq", "p_{X}(x) = (2^{x}/x!)∫_{0}^{∞} y^{x}e^{−3y} dy"),
    ("texto", "Em separado (Γ, subst. u = 3y):  ∫_{0}^{∞} y^{x}e^{−3y} dy = Γ(x + 1)/3^{x+1} = x!/3^{x+1}"),
    ("eq", "p_{X}(x) = (2^{x}/x!)·x!/3^{x+1} = 2^{x}/3^{x+1} = (1/3)(2/3)^{x}"),
    ("res", "p_{X}(x) = (1/3)(2/3)^{x},  x = 0, 1, ...   ⇒   X ~ Geométrica(p = 1/3)"),
    ("item", "c) Igualdade básica: E[E(X | Y)] = E(X)"),
    ("eq", "E(X | Y) = 2Y   ⇒   E[E(X | Y)] = 2E(Y) = 2·1 = 2"),
    ("eq", "E(X) = Σ_{x} x(1/3)(2/3)^{x} = (1/3)·(2/3)/(1 − 2/3)² = (1/3)(2/3)(9) = 2   (Σ x r^{x} = r/(1−r)²)"),
    ("res", "E[E(X | Y)] = 2 = E(X)   ✓"),
]

R[27] = [
    ("texto", "var(X + Y) = 0  ⇒  X + Y = c (constante) com probabilidade 1  ⇒  Y = c − X."),
    ("texto", "Supondo var(X) > 0 (senão ρ não está definido):"),
    ("eq", "var(Y) = var(c − X) = var(X)"),
    ("eq", "cov(X, Y) = cov(X, c − X) = cov(X, c) − cov(X, X) = 0 − var(X) = −var(X)"),
    ("eq", "ρ = cov(X, Y)/√(var X · var Y) = −var(X)/var(X)"),
    ("res", "ρ_{X,Y} = −1"),
]

R[28] = [
    ("texto", "Definição condicional:  cov(X, Y | Z) = E(XY | Z) − E(X | Z)E(Y | Z)."),
    ("item", "Termo 1"),
    ("eq", "E[cov(X, Y | Z)] = E[E(XY | Z)] − E[E(X | Z)E(Y | Z)] = E(XY) − E[E(X | Z)E(Y | Z)]"),
    ("item", "Termo 2  (E[E(X | Z)] = E(X) e E[E(Y | Z)] = E(Y))"),
    ("eq", "cov[E(X | Z), E(Y | Z)] = E[E(X | Z)E(Y | Z)] − E(X)E(Y)"),
    ("item", "Somando  (o termo E[E(X | Z)E(Y | Z)] cancela)"),
    ("eq", "E[cov(X, Y | Z)] + cov[E(X | Z), E(Y | Z)] = E(XY) − E(X)E(Y) = cov(X, Y)"),
    ("res", "cov(X, Y) = E[cov(X, Y | Z)] + cov[E(X | Z), E(Y | Z)]   ∎"),
    ("texto", "Com X = Y recupera-se a fórmula da variância total (Q23)."),
]


def montar_conteudo() -> list[tuple[str, str]]:
    enunciados = extrair_enunciados()
    conteudo = [("titulo", "Lista 2 – CE308 Teoria da Probabilidade 2 – Resolução"), ("espaco", "")]
    for n in range(1, 29):
        conteudo.append(("titulo", f"Questão {n}"))
        conteudo.append(("enunciado", enunciados[n]))
        conteudo.extend(R[n])
        conteudo.append(("espaco", ""))
    return conteudo


# ════════════════════════════ PAGINAÇÃO E SAÍDA ════════════════════════════
def paginate(content, book, rules):
    """Distribui as linhas pelas pautas; devolve uma lista de páginas."""
    max_w = PAGE_W - RIGHT_PAD - TEXT_X
    pages, cur, row = [], [], 0
    cap = len(rules)
    for kind, text in content:
        if kind == "espaco":
            if row:
                row += 1
            continue
        st = STYLES[kind]
        xh = X_HEIGHT * st["scale"]
        indent = st["indent"] * INDENT
        toks = raw_tokens(text) if kind == "enunciado" else parse(text)
        lines = wrap(toks, xh, book, max_w - indent, hang=INDENT // 2)
        need = len(lines) + (2 if kind in ("titulo", "item") else 0)  # evita título órfão
        if kind != "enunciado" and row + need > cap and row > 0:
            pages.append(cur)
            cur, row = [], 0
        for k, tk in enumerate(lines):
            if row >= cap:
                pages.append(cur)
                cur, row = [], 0
            cur.append((kind, tk, indent + (INDENT // 2 if k else 0), row))
            row += 1
    if cur:
        pages.append(cur)
    return pages


def main() -> None:
    random.seed(SEED)
    rnd = random.Random(SEED)
    book = make_book()
    rules = list(range(FIRST_RULE, PAGE_H - BOTTOM_PAD, LINE_GAP))
    pages = paginate(montar_conteudo(), book, rules)
    total = len(pages)
    for n, ops in enumerate(pages, 1):
        page = blank_page(rules, rnd, book)
        draw = ImageDraw.Draw(page)
        for kind, toks, indent, row in ops:
            st = STYLES[kind]
            xh = X_HEIGHT * st["scale"]
            ink = INKS[st["ink"]]
            x0 = TEXT_X + indent + random.randint(-2, 2)       # imperfeição em X
            base = rules[row] - 6 + random.randint(-2, 2)      # imperfeição em Y
            w = draw_line_of_text(page, toks, x0, base, xh, ink, book, rnd)
            if st["underline"]:
                hand_line(draw, (x0 - 4, base + 10), (x0 + w + 8, base + 8),
                          vary(ink, rnd) + (235,), 3, rnd)
            if st["box"]:
                l, r = x0 - 12, x0 + w + 24
                t, b = base - 2.35 * xh, base + 0.75 * xh
                c = vary(ink, rnd) + (230,)
                o = lambda: rnd.uniform(3, 8)  # cantos que "passam do ponto"
                hand_line(draw, (l - o(), t), (r + o(), t + rnd.uniform(-2, 2)), c, 2, rnd, 1.0)
                hand_line(draw, (l - o(), b), (r + o(), b + rnd.uniform(-2, 2)), c, 2, rnd, 1.0)
                hand_line(draw, (l, t - o()), (l + rnd.uniform(-2, 2), b + o()), c, 2, rnd, 0.7)
                hand_line(draw, (r, t - o()), (r + rnd.uniform(-2, 2), b + o()), c, 2, rnd, 0.7)
        draw_line_of_text(page, parse(f"{n}/{total}"), PAGE_W - RIGHT_PAD - 80,
                          PAGE_H - 45, X_HEIGHT * 0.9, INKS["preta"], book, rnd)
        page.convert("RGB").save(f"{OUT_PREFIX}_{n}.png", dpi=(200, 200))


if __name__ == "__main__":
    main()
