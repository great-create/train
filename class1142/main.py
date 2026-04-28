import sys

def main():
    data = sys.stdin.buffer.read().split()
    if not data:
        return

    it = iter(data)
    n = int(next(it))
    _L = int(next(it))

    # 一次轉 int，避免重複字串轉整數
    A = [[int(next(it)) for _ in range(n)] for _ in range(n)]
    B = [[int(next(it)) for _ in range(n)] for _ in range(n)]

    # 轉置 B，讓原本 B[k][j] 變成 BT[j][k]
    # 之後乘法時兩列連續讀取，減少索引成本
    BT = list(map(list, zip(*B)))
    del B

    C = []
    range_n = range(n)

    for i in range_n:
        Ai = A[i]
        row = []

        for j in range_n:
            Bj = BT[j]
            s = 0

            # local variable + while 比三層 list 索引更省
            k = 0
            while k < n:
                a = Ai[k]
                if a:          # 若 A 有 0，可省掉大整數乘法
                    b = Bj[k]
                    if b:
                        s += a * b
                k += 1

            row.append(str(s))

        C.append(" ".join(row))

    sys.stdout.write("\n".join(C))

if __name__ == "__main__":
    main()
