import sys
sys.set_int_max_str_digits(0)

THRESHOLD = 4

def _std(A, B, n):
    C = [[0] * n for _ in range(n)]
    for i in range(n):
        Ci = C[i]; Ai = A[i]
        for k in range(n):
            aik = Ai[k]
            if aik == 0: continue
            Bk = B[k]
            for j in range(n): Ci[j] += aik * Bk[j]
    return C

def _add(A, B, h): return [[A[i][j]+B[i][j] for j in range(h)] for i in range(h)]
def _sub(A, B, h): return [[A[i][j]-B[i][j] for j in range(h)] for i in range(h)]

def _strassen(A, B, n):
    if n <= THRESHOLD: return _std(A, B, n)
    h = n >> 1
    a11=[r[:h] for r in A[:h]]; a12=[r[h:] for r in A[:h]]
    a21=[r[:h] for r in A[h:]]; a22=[r[h:] for r in A[h:]]
    b11=[r[:h] for r in B[:h]]; b12=[r[h:] for r in B[:h]]
    b21=[r[:h] for r in B[h:]]; b22=[r[h:] for r in B[h:]]
    M1=_strassen(_add(a11,a22,h),_add(b11,b22,h),h)
    M2=_strassen(_add(a21,a22,h),b11,h)
    M3=_strassen(a11,_sub(b12,b22,h),h)
    M4=_strassen(a22,_sub(b21,b11,h),h)
    M5=_strassen(_add(a11,a12,h),b22,h)
    M6=_strassen(_sub(a21,a11,h),_add(b11,b12,h),h)
    M7=_strassen(_sub(a12,a22,h),_add(b21,b22,h),h)
    c11=_add(_sub(_add(M1,M4,h),M5,h),M7,h)
    c12=_add(M3,M5,h); c21=_add(M2,M4,h)
    c22=_add(_sub(_add(M1,M3,h),M2,h),M6,h)
    return [c11[i]+c12[i] for i in range(h)]+[c21[i]+c22[i] for i in range(h)]

def matmul(A, B, n):
    p = 1
    while p < n: p <<= 1
    if p == n: return _strassen(A, B, n)
    zero_col = [0]*(p-n)
    Ap = [r+zero_col for r in A]+[[0]*p for _ in range(p-n)]
    Bp = [r+zero_col for r in B]+[[0]*p for _ in range(p-n)]
    C_full = _strassen(Ap, Bp, p)
    return [C_full[i][:n] for i in range(n)]

def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    idx += 1  # skip L
    A = [[int(data[idx+i*n+j]) for j in range(n)] for i in range(n)]; idx += n*n
    B = [[int(data[idx+i*n+j]) for j in range(n)] for i in range(n)]
    C = matmul(A, B, n)
    sys.stdout.write('\n'.join(' '.join(str(C[i][j]) for j in range(n)) for i in range(n))+'\n')

main()
