import sys

def main():
    data = sys.stdin.buffer.read().split()
    N = int(data[0]); Tmax = int(data[1]); idx = 2
    p = [0]*N; s = [0]*N
    for i in range(N):
        p[i] = int(data[idx]); s[i] = int(data[idx+1]); idx += 2
    t = [None]*N
    for i in range(N):
        base = idx + i*N
        t[i] = [int(x) for x in data[base:base+N]]
    del data
    INF = 1 << 62

    succ = [0]*N
    pred = [0]*N
    served = bytearray(N); served[0] = 1
    bd = [INF]*N; left = [-1]*N

    def recompute(k):
        best = INF; bl = -1; a = 0; sk = s[k]; tk = t[k]
        while True:
            b = succ[a]; ta = t[a]; tak = ta[k]
            if tak:
                tkb = tk[b]
                if tkb or k == b:
                    d = tak + sk + tkb - ta[b]
                    if d < best: best = d; bl = a
            a = b
            if a == 0: break
        bd[k] = best; left[k] = bl

    # 貪婪插入：把尚未服務、可插入的客戶逐一放入；
    # 每步挑「獎勵 / 增加時間」比值最高者，增時<=0(免費)者最優先。
    def greedy_fill(cur):
        active = [k for k in range(1, N) if not served[k]]
        for k in active: recompute(k)
        while active:
            sel = -1; bnum = 0; bden = 0; infr = -1; sinf = False
            for k in active:
                d = bd[k]
                if d >= INF or cur + d > Tmax: continue
                pk = p[k]
                if d <= 0:
                    if pk > infr: infr = pk; sel = k; sinf = True
                    continue
                if sinf: continue
                if bden == 0 or pk*bden > bnum*d or (pk*bden == bnum*d and pk > bnum):
                    bnum = pk; bden = d; sel = k
            if sel < 0: break
            a = left[sel]; b = succ[a]
            succ[a] = sel; succ[sel] = b; pred[sel] = a; pred[b] = sel
            cur += bd[sel]; served[sel] = 1; active.remove(sel)
            m = sel; tm = t[m]; ta = t[a]; tam = ta[m]; tmb = tm[b]
            for k in active:
                if left[k] == a:
                    recompute(k)
                else:
                    sk = s[k]; tak = ta[k]
                    if tak:
                        tkm = t[k][m]
                        if tkm:
                            d = tak + sk + tkm - tam
                            if d < bd[k]: bd[k] = d; left[k] = a
                    tmk = tm[k]
                    if tmk:
                        tkb = t[k][b]
                        if tkb or k == b:
                            d = tmk + sk + tkb - tmb
                            if d < bd[k]: bd[k] = d; left[k] = m
        return cur

    # Or-opt(1) 重定位：把單一已服務客戶移到更省時的位置，騰出時間以便再塞入更多客戶。
    # 僅在所有新生邊(含橋接邊 pv->nv)皆為實際道路時才執行，保證路徑永遠合法。
    def relocate_pass(cur):
        improved = False
        v = succ[0]
        while v != 0:
            nxt = succ[v]
            pv = pred[v]; nv = succ[v]; tv = t[v]
            bridge = t[pv][nv]
            if bridge or pv == nv:
                saved = t[pv][v] + tv[nv] - bridge
                if saved > 0:
                    best_gain = 0; ba = -1; a = 0
                    while True:
                        b = succ[a]
                        if a != v and b != v and not (a == pv and b == nv):
                            ta = t[a]; tav = ta[v]
                            if tav:
                                tvb = tv[b]
                                if tvb:
                                    gain = saved - (tav + tvb - ta[b])
                                    if gain > best_gain: best_gain = gain; ba = a
                        a = b
                        if a == 0: break
                    if ba >= 0:
                        succ[pv] = nv; pred[nv] = pv
                        bb = succ[ba]
                        succ[ba] = v; pred[v] = ba; succ[v] = bb; pred[bb] = v
                        cur -= best_gain; improved = True
            v = nxt
        return cur, improved

    cur = greedy_fill(0)
    # 重定位 + 再填充：迴圈會自然收斂（cur 嚴格遞減、服務數單調遞增），
    # 迭代上限 1000 僅為防呆，實際大測資數次內即收斂。
    it = 0
    while N > 50 and it < 1000:
        it += 1
        cur, imp = relocate_pass(cur)
        before = sum(served)
        cur = greedy_fill(cur)
        if not imp and sum(served) == before: break

    route = [0]; a = succ[0]
    while a != 0: route.append(a); a = succ[a]
    route.append(0)
    total = 0
    for n in route: total += p[n]
    w = sys.stdout.write
    w(str(total)); w("\n"); w(" ".join(map(str, route))); w("\n")

main()
