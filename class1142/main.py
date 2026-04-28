import sys

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
        row = [int(x) for x in data[idx:idx+n]]
        A.append(row)
        idx += n

    B = []
    for _ in range(n):
        row = [int(x) for x in data[idx:idx+n]]
        B.append(row)
        idx += n

    BT = list(zip(*B))
    del B, data

    out = []
    range_n = range(n)

    for i in range_n:
        Ai = A[i]
        crow = []

        for j in range_n:
            Bj = BT[j]
            s = 0

            for k in range_n:
                a = Ai[k]
                if a:
                    b = Bj[k]
                    if b:
                        s += a * b

            crow.append(str(s))

        out.append(" ".join(crow))

    sys.stdout.write("\n".join(out))

if __name__ == "__main__":
    main()
