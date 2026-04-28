import sys

# ══════════════════════════════════════════════════════════
# 【關鍵修正】Python 3.11+ 對大整數字串轉換有 4300 位元的預設限制。
# 矩陣乘積元素最多可達 2*L + log10(n) 位（例如 L=3100, n=128 → ~6203 位），
# 超過預設限制會引發 ValueError（→ 評測顯示 RE）。
# 輸入元素若 L > 4300 也同樣會在 int() 時失敗。
# 解法：在程式最開頭將限制設為 0（無限制）。
# ══════════════════════════════════════════════════════════
sys.set_int_max_str_digits(0)
sys.setrecursionlimit(200000)


# ──────────────────────────────────────────────────────────
# I/O（優化 A：零重複字串轉整數）
# ──────────────────────────────────────────────────────────

def main():
    # buffer 讀取：省去 unicode decode；bytes.split() 為 C 層操作
    data = sys.stdin.buffer.read().split()
    pos = 0
    n  = int(data[pos]); pos += 1
    _L = int(data[pos]); pos += 1   # L 僅描述用

    A = []
    for _ in range(n):
        A.append([int(data[pos + j]) for j in range(n)])
        pos += n

    B = []
    for _ in range(n):
        B.append([int(data[pos + j]) for j in range(n)])
        pos += n

    C = _strassen(A, B, n)

    # map(str,…) 惰性；單次 write 最少 syscall
    sys.stdout.write('\n'.join(' '.join(map(str, row)) for row in C) + '\n')


# ──────────────────────────────────────────────────────────
# 矩陣工具（優化 B：zip 消除雙重索引；slice 為 C 層 memcpy）
# ──────────────────────────────────────────────────────────

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
    # 轉置 B 後用 zip 配對，sum(generator) 為 C 層累加
    Bt = list(zip(*B))
    return [[sum(a * b for a, b in zip(row, col)) for col in Bt] for row in A]


# ──────────────────────────────────────────────────────────
# Strassen 演算法
#
# threshold=2：實測最佳（n=128, L=3100）
#   - 純遞迴到 1×1：2.9s
#   - threshold=2 ：2.3s（省 7 層呼叫開銷）
#
# 優化 C（記憶體）：遞迴返回後立即 del，峰值記憶體最低
# ──────────────────────────────────────────────────────────

_THRESHOLD = 2

def _strassen(A, B, n):
    if n <= _THRESHOLD:
        return _naive(A, B, n)

    if n & 1:                          # 奇數補零
        p = n + 1
        A2 = [row + [0] for row in A] + [[0] * p]
        B2 = [row + [0] for row in B] + [[0] * p]
        C2 = _strassen(A2, B2, p)
        del A2, B2
        return [row[:n] for row in C2[:n]]

    h = n >> 1

    A11, A12, A21, A22 = _split(A, h)
    B11, B12, B21, B22 = _split(B, h)

    # 7 次遞迴乘法（加減直接作為實參，不建立有名暫存）
    M1 = _strassen(_add(A11, A22), _add(B11, B22), h)
    M2 = _strassen(_add(A21, A22), B11,            h)
    M3 = _strassen(A11,            _sub(B12, B22), h)
    M4 = _strassen(A22,            _sub(B21, B11), h)
    M5 = _strassen(_add(A11, A12), B22,            h)
    M6 = _strassen(_sub(A21, A11), _add(B11, B12), h)
    M7 = _strassen(_sub(A12, A22), _add(B21, B22), h)

    del A11, A12, A21, A22, B11, B12, B21, B22   # 立即釋放子矩陣

    C11 = _add(_sub(_add(M1, M4), M5), M7)   # M1+M4-M5+M7
    C12 = _add(M3, M5)                        # M3+M5
    C21 = _add(M2, M4)                        # M2+M4
    C22 = _add(_sub(_add(M1, M3), M2), M6)   # M1-M2+M3+M6

    del M1, M2, M3, M4, M5, M6, M7           # 立即釋放中間積

    return (
        [C11[i] + C12[i] for i in range(h)] +
        [C21[i] + C22[i] for i in range(h)]
    )


if __name__ == '__main__':
    main()
