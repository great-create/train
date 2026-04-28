import sys

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


THRESHOLD = 32


def standard_mul(A, B, n):
    BT = list(zip(*B))
    C = [[0] * n for _ in range(n)]

    rn = range(n)
    for i in rn:
        Ai = A[i]
        Ci = C[i]
        for j in rn:
            Bj = BT[j]
            s = 0
            for k in rn:
                a = Ai[k]
                if a:
                    b = Bj[k]
                    if b:
                        s += a * b
            Ci[j] = s
    return C


def add_mat(A, B, n):
    return [[A[i][j] + B[i][j] for j in range(n)] for i in range(n)]


def sub_mat(A, B, n):
    return [[A[i][j] - B[i][j] for j in range(n)] for i in range(n)]


def strassen(A, B, n):
    if n <= THRESHOLD:
        return standard_mul(A, B, n)

    m = n // 2

    A11 = [row[:m] for row in A[:m]]
    A12 = [row[m:] for row in A[:m]]
    A21 = [row[:m] for row in A[m:]]
    A22 = [row[m:] for row in A[m:]]

    B11 = [row[:m] for row in B[:m]]
    B12 = [row[m:] for row in B[:m]]
    B21 = [row[:m] for row in B[m:]]
    B22 = [row[m:] for row in B[m:]]

    M1 = strassen(add_mat(A11, A22, m), add_mat(B11, B22, m), m)
    M2 = strassen(add_mat(A21, A22, m), B11, m)
    M3 = strassen(A11, sub_mat(B12, B22, m), m)
    M4 = strassen(A22, sub_mat(B21, B11, m), m)
    M5 = strassen(add_mat(A11, A12, m), B22, m)
    M6 = strassen(sub_mat(A21, A11, m), add_mat(B11, B12, m), m)
    M7 = strassen(sub_mat(A12, A22, m), add_mat(B21, B22, m), m)

    C = [[0] * n for _ in range(n)]

    for i in range(m):
        C_i = C[i]
        C_im = C[i + m]

        M1i = M1[i]
        M2i = M2[i]
        M3i = M3[i]
        M4i = M4[i]
        M5i = M5[i]
        M6i = M6[i]
        M7i = M7[i]

        for j in range(m):
            c11 = M1i[j] + M4i[j] - M5i[j] + M7i[j]
            c12 = M3i[j] + M5i[j]
            c21 = M2i[j] + M4i[j]
            c22 = M1i[j] - M2i[j] + M3i[j] + M6i[j]

            C_i[j] = c11
            C_i[j + m] = c12
            C_im[j] = c21
            C_im[j + m] = c22

    return C


def next_power_of_two(n):
    p = 1
    while p < n:
        p <<= 1
    return p


def pad_matrix(M, n, size):
    if size == n:
        return M

    Z = []
    for i in range(n):
        Z.append(M[i] + [0] * (size - n))

    zero_row = [0] * size
    for _ in range(size - n):
        Z.append(zero_row[:])

    return Z


def main():
    data = sys.stdin.buffer.read().split()
    if not data:
        return

    n = int(data[0])
    idx = 2

    A = []
    for _ in range(n):
        A.append([int(x) for x in data[idx:idx + n]])
        idx += n

    B = []
    for _ in range(n):
        B.append([int(x) for x in data[idx:idx + n]])
        idx += n

    del data

    size = next_power_of_two(n)

    if size != n:
        A = pad_matrix(A, n, size)
        B = pad_matrix(B, n, size)

    C = strassen(A, B, size)

    out = []
    for i in range(n):
        out.append(" ".join(str(C[i][j]) for j in range(n)))

    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()
