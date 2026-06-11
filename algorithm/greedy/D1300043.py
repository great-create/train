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

    succ = [0]*N; pred = [0]*N
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

    # Or-opt(L)：把連續 L 個客戶整段(不反轉)搬到更省時的位置。
    # 內部邊不變，只換 3 條邊(橋接 pv->nv、新左 a->h、新右 t_->b)，全部須為實路。
    def oropt_pass(cur, L):
        improved = False
        h = succ[0]                     # 段頭
        while h != 0:
            # 取出長度 L 的段 h..tail
            tail = h; ok = True
            for _ in range(L-1):
                tail = succ[tail]
                if tail == 0: ok = False; break
            nxt_after = succ[tail]
            if not ok:
                break
            pv = pred[h]; nv = succ[tail]
            bridge = t[pv][nv]
            if (bridge or pv == nv):
                saved = t[pv][h] + t[tail][nv] - bridge
                if saved > 0:
                    best_gain = 0; ba = -1; a = 0
                    t_tail = t[tail]
                    while True:
                        b = succ[a]
                        # a,b 不可落在段內或原位
                        inside = False
                        x = h
                        while True:
                            if a == x or b == x: inside = True; break
                            if x == tail: break
                            x = succ[x]
                        if not (inside or (a == pv and b == nv)):
                            ta = t[a]; tah = ta[h]
                            if tah:
                                ttb = t_tail[b]
                                if ttb:
                                    gain = saved - (tah + ttb - ta[b])
                                    if gain > best_gain: best_gain = gain; ba = a
                        a = b
                        if a == 0: break
                    if ba >= 0:
                        # 拆段
                        succ[pv] = nv; pred[nv] = pv
                        bb = succ[ba]
                        succ[ba] = h; pred[h] = ba
                        succ[tail] = bb; pred[bb] = tail
                        cur -= best_gain; improved = True
            h = nxt_after
        return cur, improved

    cur = greedy_fill(0)
    it = 0
    while N > 50 and it < 1000:
        it += 1
        imp_any = False
        for L in (1, 2, 3):
            cur, imp = oropt_pass(cur, L)
            imp_any = imp_any or imp
        before = sum(served)
        cur = greedy_fill(cur)
        if not imp_any and sum(served) == before: break

    route = [0]; a = succ[0]
    while a != 0: route.append(a); a = succ[a]
    route.append(0)
    total = 0
    for n in route: total += p[n]
    w = sys.stdout.write
    w(str(total)); w("\n"); w(" ".join(map(str, route))); w("\n")

main()
