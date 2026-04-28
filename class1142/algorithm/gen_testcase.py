"""
在 judge 機器上直接執行此腳本，生成測資與答案。
用法：python3 gen_testcase.py
會產生 hard_test.in 和 hard_test.out 在同一目錄。
"""
import sys, random, os
sys.set_int_max_str_digits(0)
sys.setrecursionlimit(200000)

# ── 參數 ──────────────────────────────────────────
N, L = 128, 3100
SEED = 777777
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
# ──────────────────────────────────────────────────

print(f'[生成測資] n={N}, L={L}', flush=True)

rng = random.Random(SEED)
A = [[rng.randint(10**(L-1), 10**L-1) for _ in range(N)] for _ in range(N)]
B = [[rng.randint(10**(L-1), 10**L-1) for _ in range(N)] for _ in range(N)]
print(f'[生成測資] 矩陣已生成', flush=True)

# ── 以下為 main.py 的核心函式（複製過來計算答案）──
_DC = {}
def _fast_dec(n, _s=str):
    if n < 10**18: return _s(n)
    hb = n.bit_length() >> 1
    ad = (hb * 30103) // 100000
    b = _DC.get(ad)
    if b is None: b = 10**ad; _DC[ad] = b
    hi, lo = divmod(n, b)
    return _fast_dec(hi) + _s(lo).zfill(ad)

def _add(A,B): return [[a+b for a,b in zip(ra,rb)] for ra,rb in zip(A,B)]
def _sub(A,B): return [[a-b for a,b in zip(ra,rb)] for ra,rb in zip(A,B)]
def _split(M,h):
    top,bot=M[:h],M[h:]
    return [r[:h] for r in top],[r[h:] for r in top],[r[:h] for r in bot],[r[h:] for r in bot]
def _naive(A,B,n):
    Bt=list(zip(*B)); return [[sum(a*b for a,b in zip(r,c)) for c in Bt] for r in A]
def _s2x2(A,B):
    a11,a12=A[0];a21,a22=A[1];b11,b12=B[0];b21,b22=B[1]
    m1=(a11+a22)*(b11+b22);m2=(a21+a22)*b11;m3=a11*(b12-b22)
    m4=a22*(b21-b11);m5=(a11+a12)*b22;m6=(a21-a11)*(b11+b12);m7=(a12-a22)*(b21+b22)
    return [[m1+m4-m5+m7,m3+m5],[m2+m4,m1-m2+m3+m6]]
def _c11(M1,M4,M5,M7):
    return [[a+d-e+g for a,d,e,g in zip(r1,r4,r5,r7)] for r1,r4,r5,r7 in zip(M1,M4,M5,M7)]
def _c22(M1,M2,M3,M6):
    return [[a-b+c+f for a,b,c,f in zip(r1,r2,r3,r6)] for r1,r2,r3,r6 in zip(M1,M2,M3,M6)]
def _best_T(n,L):
    if L<=0: return min(n,32)
    raw=max(2,int(8.5/(L**0.29))+1); p=1
    while p<raw: p<<=1
    return min(p,n)
def _strassen(A,B,n,T):
    if n==2: return _s2x2(A,B)
    if n==1: return [[A[0][0]*B[0][0]]]
    if n<=T: return _naive(A,B,n)
    if n&1:
        p=n+1;A2=[r+[0] for r in A]+[[0]*p];B2=[r+[0] for r in B]+[[0]*p]
        C2=_strassen(A2,B2,p,T);del A2,B2;return [r[:n] for r in C2[:n]]
    h=n>>1
    A11,A12,A21,A22=_split(A,h);B11,B12,B21,B22=_split(B,h)
    M1=_strassen(_add(A11,A22),_add(B11,B22),h,T);M2=_strassen(_add(A21,A22),B11,h,T)
    M3=_strassen(A11,_sub(B12,B22),h,T);M4=_strassen(A22,_sub(B21,B11),h,T)
    M5=_strassen(_add(A11,A12),B22,h,T);M6=_strassen(_sub(A21,A11),_add(B11,B12),h,T)
    M7=_strassen(_sub(A12,A22),_add(B21,B22),h,T)
    del A11,A12,A21,A22,B11,B12,B21,B22
    C11=_c11(M1,M4,M5,M7);C12=_add(M3,M5);C21=_add(M2,M4);C22=_c22(M1,M2,M3,M6)
    del M1,M2,M3,M4,M5,M6,M7
    return [C11[i]+C12[i] for i in range(h)]+[C21[i]+C22[i] for i in range(h)]

T = _best_T(N, L)
print(f'[計算中] Strassen T={T}...', flush=True)
C = _strassen(A, B, N, T)
print(f'[計算完成]', flush=True)

# ── 寫 .in ────────────────────────────────────────
path_in  = os.path.join(OUT_DIR, 'hard_test.in')
path_out = os.path.join(OUT_DIR, 'hard_test.out')

print(f'[寫入] {path_in}', flush=True)
with open(path_in, 'w') as f:
    f.write(f'{N} {L}\n')
    for row in A: f.write(' '.join(map(str, row)) + '\n')
    for row in B: f.write(' '.join(map(str, row)) + '\n')

# ── 寫 .out ───────────────────────────────────────
log_n   = (N.bit_length() * 30103) // 100000 if N > 1 else 0
out_dig = 2 * L + log_n + 1
to_str  = _fast_dec if out_dig > 4000 else str

print(f'[寫入] {path_out}  (每元素 ~{out_dig} 位)', flush=True)
with open(path_out, 'w') as f:
    for i, row in enumerate(C):
        if i: f.write('\n')
        f.write(' '.join(to_str(x) for x in row))
    f.write('\n')

sz_in  = os.path.getsize(path_in)
sz_out = os.path.getsize(path_out)
print(f'[完成] hard_test.in  {sz_in/1e6:.0f} MB', flush=True)
print(f'[完成] hard_test.out {sz_out/1e6:.0f} MB', flush=True)
print(f'')
print(f'測試指令：')
print(f'  time python3 main.py < hard_test.in > my_out.txt')
print(f'  diff my_out.txt hard_test.out && echo AC || echo WA')
