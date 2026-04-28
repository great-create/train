import sys

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def main():
    data = sys.stdin.buffer.read().split()
    if not data:
        return

    n = int(data[0])

    # 相容兩種格式：
    # 1. n L
    # 2. 只有 n
    if len(data) == 1 + 2 * n * n:
        idx = 1
    else:
        idx = 2

    A = []
    for _ in range(n):
        row = [int(x) for x in data[idx:idx + n]]
        A.append(row)
        idx += n

    B = []
    b_zero_count = 0
    for _ in range(n):
        row = []
        for x in data[idx:idx + n]:
            if x == b"0":
                row.append(0)
                b_zero_count += 1
            else:
                row.append(int(x))
        B.append(row)
        idx += n

    del data

    rn = range(n)

    # 若 B 很多 0，使用稀疏乘法
    if b_zero_count > n * n // 4:
        Bnz = []
        for k in rn:
            nz = []
            Bk = B[k]
            for j in rn:
                b = Bk[j]
                if b:
                    nz.append((j, b))
            Bnz.append(nz)

        del B

        for i in rn:
            Ai = A[i]
            Ci = [0] * n

            for k in rn:
                a = Ai[k]
                if a:
                    for j, b in Bnz[k]:
                        Ci[j] += a * b

            line = " ".join(map(str, Ci))
            sys.stdout.write(line)
            if i != n - 1:
                sys.stdout.write("\n")

    # 若 B 不稀疏，使用轉置版標準乘法
    else:
        BT = list(zip(*B))
        del B

        for i in rn:
            Ai = A[i]
            out_row = []

            for j in rn:
                Bj = BT[j]
                s = 0

                for k in rn:
                    s += Ai[k] * Bj[k]

                out_row.append(str(s))

            sys.stdout.write(" ".join(out_row))
            if i != n - 1:
                sys.stdout.write("\n")


if __name__ == "__main__":
    main()
