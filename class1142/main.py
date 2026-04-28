import sys

sys.set_int_max_str_digits(0)   # 允許超過 4300 位的大整數字串轉換（Python 3.11+ 預設限制）
sys.setrecursionlimit(200000)

# ══════════════════════════════════════════════════════════
#  快速整數轉十進位字串（Divide-and-Conquer，O(D log²D)）
#  用途：舊版 Python 的 str(big_int) 是 O(D²)，此函式保持快速。
#  實作：以 bit_length() 估算十進位位數，不使用 math 模組。
# ══════════════════════════════════════════════════════════
_DEC_CACHE: dict = {}

def _fast_dec(n: int, _str=str) -> str:
    if n < 10**18:          # 小數直接用內建 str()（已足夠快）
        return _str(n)
    # floor(bit_length * log10(2)) ≈ floor(bit_length * 30103/100000)
    half_bits   = n.bit_length() >> 1
    approx_d    = (half_bits * 30103) // 100000   # 切割點（十進位位數）
    base        = _DEC_CACHE.get(approx_d)
    if base is None:
        base = 10 ** approx_d
        _DEC_CACHE[approx_d] = base
    hi, lo = divmod(n, base)
    return _fast_dec(hi) + _str(lo).zfill(approx_d)


# ══════════════════════════════════════════════════════════
#  自適應 Strassen 閾值（依 L 決定切換至樸素乘法的規模）
#
#  Strassen 每層：7 次乘法 + 18 次加減
#  乘法成本 ∝ L^1.585；加法成本 ∝ L
#  L 小 → 加法相對貴 → 閾值要大（減少遞迴層）
#  L 大 → 乘法主導  → 閾值要小（多省乘法）
#
#  推導：最佳 T ≈ ceil(8.5 / L^0.29)，取 2 的冪次
#    L=1     → T=32   （比固定 T=2 快 10×）
#    L=10    → T=8    （快 4×）
#    L=100   → T=4    （快 1.5×）
#    L=1000+ → T=2    （已最佳）
# ══════════════════════════════════════════════════════════
def _best_threshold(n: int, L: int) -> int:
    if L <= 0:
        return min(n, 32)
    raw = max(2, int(8.5 / (L ** 0.29)) + 1)  # L**0.29 是純 Python 運算子
    p = 1
    while p < raw:
        p <<= 1          # 取最近的 2 的冪次
    return min(p, n)


# ══════════════════════════════════════════════════════════
#  矩陣工具（zip / slice 消除雙重 [i][j] 索引）
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
    Bt = list(zip(*B))          # 轉置 B，提升快取命中
    return [[sum(a * b for a, b in zip(row, col)) for col in Bt] for row in A]


# ══════════════════════════════════════════════════════════
#  Strassen 主體（遞迴後立即 del 釋放中間矩陣）
# ══════════════════════════════════════════════════════════
def _strassen(A, B, n, T):
    if n <= T:
        return _naive(A, B, n)

    if n & 1:                           # 奇數補零
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

    del A11, A12, A21, A22, B11, B12, B21, B22

    C11 = _add(_sub(_add(M1, M4), M5), M7)
    C12 = _add(M3, M5)
    C21 = _add(M2, M4)
    C22 = _add(_sub(_add(M1, M3), M2), M6)

    del M1, M2, M3, M4, M5, M6, M7

    return (
        [C11[i] + C12[i] for i in range(h)] +
        [C21[i] + C22[i] for i in range(h)]
    )


# ══════════════════════════════════════════════════════════
#  主程式
# ══════════════════════════════════════════════════════════
def main():
    data = sys.stdin.buffer.read().split()
    pos  = 0
    n    = int(data[pos]); pos += 1
    L    = int(data[pos]); pos += 1

    A = []
    for _ in range(n):
        A.append([int(data[pos + j]) for j in range(n)])
        pos += n

    B = []
    for _ in range(n):
        B.append([int(data[pos + j]) for j in range(n)])
        pos += n

    T = _best_threshold(n, L)
    C = _strassen(A, B, n, T)

    # 輸出元素位數 ≈ 2*L + log10(n)
    # 用 bit_length 估算：若 n>1，n.bit_length()*30103//100000 ≈ floor(log10(n))
    log_n   = (n.bit_length() * 30103) // 100000 if n > 1 else 0
    out_dig = 2 * L + log_n + 1
    to_str  = _fast_dec if out_dig > 4000 else str

    out = sys.stdout.buffer
    for i, row in enumerate(C):
        if i:
            out.write(b'\n')
        out.write(b' '.join(to_str(x).encode() for x in row))
    out.write(b'\n')


if __name__ == '__main__':
    main()
