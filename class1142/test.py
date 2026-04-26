import sys


def read_input():
    data = sys.stdin.buffer.read().split()

    n = int(data[0])
    # L = int(data[1])  # 題目給 L，但計算時不需要用到

    idx = 2

    A = []
    for _ in range(n):
        row = [int(x) for x in data[idx:idx + n]]
        A.append(row)
        idx += n

    B = []
    for _ in range(n):
        row = [int(x) for x in data[idx:idx + n]]
        B.append(row)
        idx += n

    return n, A, B


def matmul_bigint(n, A, B):
    """
    計算 C = A x B

    使用策略：
    1. dense 情況：row-based i-k-j
    2. B 若有不少 0：建立 B 的非零元素表，跳過乘 0
    """

    total = n * n

    # 統計 B 的非零元素數量，用來決定是否採用 sparse B 優化
    nnz_b = 0
    for row in B:
        for x in row:
            if x:
                nnz_b += 1

    # 若 B 的非零比例較低，使用 sparse row 優化
    # 門檻可依測資調整，這裡用 75% 作為保守判斷
    if nnz_b * 4 < total * 3:
        B_nonzero = []
        for row in B:
            pairs = []
            for j, value in enumerate(row):
                if value:
                    pairs.append((j, value))
            B_nonzero.append(pairs)

        C = []
        for rowA in A:
            crow = [0] * n

            for k, a in enumerate(rowA):
                if a:
                    for j, b in B_nonzero[k]:
                        crow[j] += a * b

            C.append(crow)

        return C

    # 一般 dense 情況
    C = []
    rng = range(n)

    for rowA in A:
        crow = [0] * n

        for k, a in enumerate(rowA):
            if a:
                brow = B[k]

                # 更新 C[i][j] += A[i][k] * B[k][j]
                for j in rng:
                    crow[j] += a * brow[j]

        C.append(crow)

    return C


def write_output(C):
    out_lines = []

    for row in C:
        out_lines.append(" ".join(str(x) for x in row))

    sys.stdout.write("\n".join(out_lines))


def main():
    n, A, B = read_input()
    C = matmul_bigint(n, A, B)
    write_output(C)


if __name__ == "__main__":
    main()
