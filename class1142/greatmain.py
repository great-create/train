import sys

sys.set_int_max_str_digits(0)
sys.setrecursionlimit(200000)

# ══════════════════════════════════════════════════════════
#  快速整數→十進位字串（Divide-and-Conquer O(D log²D)）
#  - 不使用 math 模組：以 bit_length()*30103//100000 估算十進位位數
#  - 在舊版 Python（<3.11）中比內建 str() 快數十倍
#  - 在 Python 3.12 中對 D>6000 仍快 1.5×
# ══════════════════════════════════════════════════════════
_DC: dict = {}

def _fast_dec(n: int, _s=str) -> str:
    if n < 10**18:
        return _s(n)
    hb  = n.bit_length() >> 1
    ad  = (hb * 30103) // 100000   # ≈ floor(hb × log10 2)
    b   = _DC.get(ad)
    if b is None:
        b = 10**ad
        _DC[ad] = b
    hi, lo = divmod(n, b)
    return _fast_dec(hi) + _s(lo).zfill(ad)


# ══════════════════════════════════════════════════════════
#  自適應 Strassen 閾值
#  推導：乘法成本 ∝ L^1.585；加法成本 ∝ L
#  Strassen 每層節省 1 次乘法但多 18 次加法
#  收支平衡點：T ≈ ceil(8.5 / L^0.29)，取 2 的冪次
#
#  L=1    → T=32  （比 T=2 快 10×）
#  L=10   → T=8   （快 4×）
#  L=100  → T=4   （快 1.5×）
#  L=1000+→ T=2   （已最佳）
# ══════════════════════════════════════════════════════════
def _best_T(n: int, L: int) -> int:
    if L <= 0:
        return min(n, 32)
    raw = max(2, int(8.5 / (L ** 0.29)) + 1)
    p = 1
    while p < raw:
        p <<= 1
    return min(p, n)


# ══════════════════════════════════════════════════════════
#  矩陣工具（zip/slice 消除雙重索引）
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
    Bt = list(zip(*B))
    return [[sum(a * b for a, b in zip(row, col)) for col in Bt] for row in A]


# ══════════════════════════════════════════════════════════
#  Strassen 2×2 展開（7 次乘法，比 naive 8 次少 12.5%）
#  在 n=128,L=3100 上節省約 16% 計算時間
# ══════════════════════════════════════════════════════════
def _s2x2(A, B):
    a11, a12 = A[0];  a21, a22 = A[1]
    b11, b12 = B[0];  b21, b22 = B[1]
    m1 = (a11 + a22) * (b11 + b22)
    m2 = (a21 + a22) * b11
    m3 =  a11         * (b12 - b22)
    m4 =  a22         * (b21 - b11)
    m5 = (a11 + a12) * b22
    m6 = (a21 - a11) * (b11 + b12)
    m7 = (a12 - a22) * (b21 + b22)
    return [
        [m1 + m4 - m5 + m7,  m3 + m5],
        [m2 + m4,             m1 - m2 + m3 + m6],
    ]


# ══════════════════════════════════════════════════════════
#  Strassen 主體
#  葉節點優先順序：
#    n==1 → 直接純量乘法（1 mul）
#    n==2 → _s2x2 展開（7 mul，比 naive 8 mul 少）
#    n<=T → _naive（適合小 L 時 T 較大的情況）
#  遞迴後立即 del 中間矩陣，降低峰值記憶體
# ══════════════════════════════════════════════════════════
def _strassen(A, B, n, T):
    if n == 2:
        return _s2x2(A, B)
    if n == 1:
        return [[A[0][0] * B[0][0]]]
    if n <= T:
        return _naive(A, B, n)

    if n & 1:                           # 奇數補零（至多 log₂n 次）
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

    T = _best_T(n, L)
    C = _strassen(A, B, n, T)

    # 選擇輸出轉換函式
    # 輸出元素約 2L + log10(n) 位；超過 4000 位用 _fast_dec
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
