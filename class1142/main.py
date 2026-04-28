import sys

# 解決 Python 3.11+ 超大整數字串限制
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def main():
    data = sys.stdin.buffer.read().split()
    if not data:
        return

    n = int(data[0])
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

    # B 轉置，讓乘法時連續讀取，降低 B[k][j] 索引成本
    BT = list(zip(*B))

    del B
    del data

    out_lines = []
    rn = range(n)

    for i in rn:
        Ai = A[i]
        ans_row = []

        for j in rn:
            Bj = BT[j]
            s = 0

            for k in rn:
                a = Ai[k]
                if a:
                    b = Bj[k]
                    if b:
                        s += a * b

            ans_row.append(str(s))

        out_lines.append(" ".join(ans_row))

    sys.stdout.write("\n".join(out_lines))


if __name__ == "__main__":
    main()
