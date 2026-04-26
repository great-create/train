import sys

def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    L = int(data[1])  # 題目給的長度限制，程式中不一定需要使用

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

    C = [[0] * n for _ in range(n)]

    # 使用 i-k-j 順序，比傳統 i-j-k 在 Python 中通常更快
    # 因為可以重複使用 A[i][k]，並且連續存取 B[k][j]
    for i in range(n):
        Ci = C[i]
        Ai = A[i]

        for k in range(n):
            aik = Ai[k]

            # 若 A[i][k] 是 0，整列乘法可省略
            if aik == 0:
                continue

            Bk = B[k]

            for j in range(n):
                if Bk[j] != 0:
                    Ci[j] += aik * Bk[j]

    out = []
    for i in range(n):
        out.append(" ".join(str(x) for x in C[i]))

    sys.stdout.write("\n".join(out))

if __name__ == "__main__":
    main()
