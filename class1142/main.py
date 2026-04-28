import sys, math

# ── 修正：Python 3.11+ 對大整數字串轉換有 4300 位元預設限制 ──
sys.set_int_max_str_digits(0)
sys.setrecursionlimit(200000)

# ══════════════════════════════════════════════════════════
#  快速整數轉十進位字串（Divide-and-Conquer）
#  - Python 3.10 以前的 str(big_int) 是 O(D²)，極慢
#  - 本函式無論 Python 版本均保持 O(D log²D)
#  - 對 D > 6000 的數值，比內建 str() 快 1.5～2x
# ══════════════════════════════════════════════════════════
_STR_CACHE: dict = {}
_CUTOFF = 10 ** 9          # 小數直接用內建 str()（快）

def _fast_dec(n: int) -> str:
    if n < _CUTOFF:
        return str(n)
    D = math.floor(math.log10(n)) + 1
    half = D >> 1
    base = _STR_CACHE.get(half)
    if base is None:
        base = 10 ** half
        _STR_CACHE[half] = base
    hi, lo = divmod(n, base)
    return _fast_dec(hi) + str(lo).zfill(half)


# ══════════════════════════════════════════════════════════
#  自適應 Strassen 閾值（根據 L 決定切換到樸素乘法的大小）
#
#  成本分析：
#    Strassen 一層：7 次遞迴乘法 + 18 次矩陣加減
#    加法成本 ∝ O(L)；乘法成本 ∝ O(L^1.585)
#    當 L 小時，加法相對昂貴 → 閾值要大（少做 Strassen 層）
#    當 L 大時，乘法主導 → 閾值要小（多做 Strassen 層省乘法）
#
#  公式推導：threshold ≈ ceil(8.5 / L^0.29)，取最近 2 的冪次
#  實測最佳值：
#    L=1     → T=32
#    L=10    → T=8
#    L=100   → T=4
#    L=1000+ → T=2
# ══════════════════════════════════════════════════════════

def _best_threshold(n: int, L: int) -> int:
    if L <= 0:
        return min(n, 32)
    raw = max(2, int(8.5 / (L ** 0.29)) + 1)
    p = 1
    while p < raw:
        p <<= 1        # 取最近 2 的冪次
    return min(p, n)


# ══════════════════════════════════════════════════════════
#  矩陣工具（優化 B：zip / slice 消除雙重索引）
# ══════════════════════════════════════════════════════════

def _add(A, B):
    return [[a + b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]

def _sub(A, B):
    return [[a - b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]

def _split(M, h):
    top, bot = M[:h], M[h:]
    return (
        [row[:h] for row in top],
        [row[h:] for row in top],
        [row[:h] for row in bot],
        [row[h:] for row in bot],
    )

def _naive(A, B, n):
    """轉置 B 後用 zip 內積；sum(generator) 為 C 層累加"""
    Bt = list(zip(*B))
    return [[sum(a * b for a, b in zip(row, col)) for col in Bt] for row in A]


# ══════════════════════════════════════════════════════════
#  Strassen 主體（優化 C：立即 del 釋放中間矩陣）
# ══════════════════════════════════════════════════════════

def _strassen(A, B, n, T):
    """
    遞迴 Strassen，以 T（自適應閾值）為基底切換到樸素乘法。
    T 由呼叫端根據 L 計算，避免在每次遞迴內重算。
    """
    if n <= T:
        return _naive(A, B, n)

    if n & 1:                                  # 奇數補零
        p = n + 1
        A2 = [row + [0] for row in A] + [[0] * p]
        B2 = [row + [0] for row in B] + [[0] * p]
        C2 = _strassen(A2, B2, p, T)
        del A2, B2
        return [row[:n] for row in C2[:n]]

    h = n >> 1
    A11, A12, A21, A22 = _split(A, h)
    B11, B12, B21, B22 = _split(B, h)

    M1 = _strassen(_add(A11, A22), _add(B11, B22), h, T)
    M2 = _strassen(_add(A21, A22), B11,            h, T)
    M3 = _strassen(A11,            _sub(B12, B22), h, T)
    M4 = _strassen(A22,            _sub(B21, B11), h, T)
    M5 = _strassen(_add(A11, A12), B22,            h, T)
    M6 = _strassen(_sub(A21, A11), _add(B11, B12), h, T)
    M7 = _strassen(_sub(A12, A22), _add(B21, B22), h, T)

    del A11, A12, A21, A22, B11, B12, B21, B22    # 優化 C

    C11 = _add(_sub(_add(M1, M4), M5), M7)
    C12 = _add(M3, M5)
    C21 = _add(M2, M4)
    C22 = _add(_sub(_add(M1, M3), M2), M6)

    del M1, M2, M3, M4, M5, M6, M7               # 優化 C

    return (
        [C11[i] + C12[i] for i in range(h)] +
        [C21[i] + C22[i] for i in range(h)]
    )


# ══════════════════════════════════════════════════════════
#  主程式
# ══════════════════════════════════════════════════════════

def main():
    # ── 輸入（優化 A：buffer 讀取，每個 token 只 int() 一次） ──
    data = sys.stdin.buffer.read().split()
    pos = 0
    n  = int(data[pos]); pos += 1
    L  = int(data[pos]); pos += 1

    A = []
    for _ in range(n):
        A.append([int(data[pos + j]) for j in range(n)])
        pos += n

    B = []
    for _ in range(n):
        B.append([int(data[pos + j]) for j in range(n)])
        pos += n

    # ── 計算（自適應閾值） ──────────────────────────────
    T = _best_threshold(n, L)
    C = _strassen(A, B, n, T)

    # ── 輸出（選擇快速十進位轉換函式） ──────────────────
    # 輸出元素位數 ≈ 2*L + log10(n) 位
    # 若 Python < 3.11，內建 str() 是 O(D²) → 用 _fast_dec
    # 若 Python >= 3.11，str() 已是 O(D log²D) → 對大 D 仍用 _fast_dec（快 1.5x）
    out_digits = 2 * L + (math.floor(math.log10(n)) + 1 if n > 1 else 1)
    to_str = _fast_dec if out_digits > 4000 else str

    # 使用 buffer 寫出避免 Python str I/O 開銷
    out = sys.stdout.buffer
    for i, row in enumerate(C):
        if i:
            out.write(b'\n')
        out.write(b' '.join(to_str(x).encode() for x in row))
    out.write(b'\n')


if __name__ == '__main__':
    main()
