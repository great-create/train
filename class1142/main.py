import sys

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def main():
    rd = sys.stdin.buffer.readline
    wr = sys.stdout.write

    first = rd().split()
    n = int(first[0])

    A = []
    for _ in range(n):
        A.append([int(x) for x in rd().split()])

    # B 不直接存完整矩陣，只存每一列的非 0 元素
    Bnz = []
    for _ in range(n):
        row = rd().split()
        nz = []
        for j, x in enumerate(row):
            if x != b"0":
                nz.append((j, int(x)))
        Bnz.append(nz)

    rn = range(n)

    for i in rn:
        Ai = A[i]
        Ci = [0] * n

        for k in rn:
            a = Ai[k]
            if a:
                bk = Bnz[k]
                if bk:
                    for j, b in bk:
                        Ci[j] += a * b

        line = " ".join(str(x) for x in Ci)

        if i + 1 < n:
            wr(line + "\n")
        else:
            wr(line)


if __name__ == "__main__":
    main()
