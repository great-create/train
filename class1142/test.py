import sys


def classical_mul(A, B, n):
    """
    傳統矩陣乘法，使用 flat list 儲存矩陣。
    A, B, C 都是長度 n*n 的一維陣列。
    """
    C = [0] * (n * n)
    rn = range(n)

    for i in rn:
        ci = i * n
        ai = i * n

        for k in rn:
            aik = A[ai + k]

            # 若 A[i][k] 是 0，這一整段乘法都可以省略
            if aik == 0:
                continue

            bk = k * n

            for j in rn:
                C[ci + j] += aik * B[bk + j]

    return C


def mat_add(A, B):
    return [a + b for a, b in zip(A, B)]


def mat_sub(A, B):
    return [a - b for a, b in zip(A, B)]


def split_matrix(M, n):
    """
    將 n*n 矩陣切成四個 n/2 * n/2 子矩陣。
    """
    h = n // 2
    size = h * h

    A11 = [0] * size
    A12 = [0] * size
    A21 = [0] * size
    A22 = [0] * size

    for i in range(h):
        src1 = i * n
        src2 = (i + h) * n
        dst = i * h

        A11[dst:dst + h] = M[src1:src1 + h]
        A12[dst:dst + h] = M[src1 + h:src1 + n]
        A21[dst:dst + h] = M[src2:src2 + h]
        A22[dst:dst + h] = M[src2 + h:src2 + n]

    return A11, A12, A21, A22


def join_matrix(C11, C12, C21, C22, n):
    """
    將四個 n/2 * n/2 子矩陣合併成 n*n 矩陣。
    """
    h = n // 2
    C = [0] * (n * n)

    for i in range(h):
        src = i * h

        dst1 = i * n
        dst2 = (i + h) * n

        C[dst1:dst1 + h] = C11[src:src + h]
        C[dst1 + h:dst1 + n] = C12[src:src + h]

        C[dst2:dst2 + h] = C21[src:src + h]
        C[dst2 + h:dst2 + n] = C22[src:src + h]

    return C


def strassen_mul(A, B, n, cutoff):
    """
    Strassen 矩陣乘法。
    當 n <= cutoff 時，改用傳統乘法。
    """
    if n <= cutoff:
        return classical_mul(A, B, n)

    h = n // 2

    A11, A12, A21, A22 = split_matrix(A, n)
    B11, B12, B21, B22 = split_matrix(B, n)

    # Strassen 的 7 個乘法
    P1 = strassen_mul(mat_add(A11, A22), mat_add(B11, B22), h, cutoff)
    P2 = strassen_mul(mat_add(A21, A22), B11, h, cutoff)
    P3 = strassen_mul(A11, mat_sub(B12, B22), h, cutoff)
    P4 = strassen_mul(A22, mat_sub(B21, B11), h, cutoff)
    P5 = strassen_mul(mat_add(A11, A12), B22, h, cutoff)
    P6 = strassen_mul(mat_sub(A21, A11), mat_add(B11, B12), h, cutoff)
    P7 = strassen_mul(mat_sub(A12, A22), mat_add(B21, B22), h, cutoff)

    # 合併四個區塊
    C11 = [p1 + p4 - p5 + p7 for p1, p4, p5, p7 in zip(P1, P4, P5, P7)]
    C12 = [p3 + p5 for p3, p5 in zip(P3, P5)]
    C21 = [p2 + p4 for p2, p4 in zip(P2, P4)]
    C22 = [p1 - p2 + p3 + p6 for p1, p2, p3, p6 in zip(P1, P2, P3, P6)]

    return join_matrix(C11, C12, C21, C22, n)


def next_power_of_two(x):
    return 1 << (x - 1).bit_length()


def main():
    data = sys.stdin.buffer.read().split()

    n = int(data[0])
    L = int(data[1])

    idx = 2

    # 若資料很大，使用 Strassen 時需要補到 2 的次方
    m = next_power_of_two(n)

    A = [0] * (m * m)
    B = [0] * (m * m)

    # 讀取 A
    for i in range(n):
        base = i * m
        for j in range(n):
            A[base + j] = int(data[idx])
            idx += 1

    # 讀取 B
    for i in range(n):
        base = i * m
        for j in range(n):
            B[base + j] = int(data[idx])
            idx += 1

    # cutoff 是效能關鍵
    # L 很大時，超大整數乘法成本高，Strassen 越有價值
    if n < 64 or L <= 64:
        # 小矩陣或小整數：傳統乘法通常比較快
        C = classical_mul(A, B, m)
    else:
        # 大矩陣 + 超大整數：使用 Strassen
        # 若記憶體不足，可把 cutoff 改成 32
        # 若時間仍太慢，可嘗試 8 或 16
        cutoff = 16
        C = strassen_mul(A, B, m, cutoff)

    # 輸出原本 n*n 的有效範圍，不輸出補 0 的區域
    out_write = sys.stdout.write

    for i in range(n):
        base = i * m
        row = [str(C[base + j]) for j in range(n)]

        if i + 1 < n:
            out_write(" ".join(row) + "\n")
        else:
            out_write(" ".join(row))


if __name__ == "__main__":
    main()
