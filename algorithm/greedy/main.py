import sys

# ============================================================================
# 限時獎勵收集配送（Orienteering）— 貪婪演算法
# 對應課堂講義 Class 4「The Greedy Approach」之三步驟框架：
#   選擇程序 (Selection Procedure)：依「單位成本最大價值」挑下一個客戶
#                                    （獎勵 p / 增加時間 Δ 最大者；對應 0-1 背包 p.52）
#   可行性檢查 (Feasibility Check) ：插入後每條邊須為實路、且總時間 <= T_max
#   解答檢查   (Solution Check)    ：沒有任何客戶還能可行插入時即得解
# 註：本問題＝0-1 背包(挑客戶)＋TSP(走法)，為 NP-hard，屬講義中
#     「貪婪不保證最佳」之類（同 0-1 背包 p.53）。小測資可達最佳，
#     大測資僅能逼近，最後再以貪婪式 Or-opt 區域改善盡量提高獎勵。
# ============================================================================

def main():
    data = sys.stdin.buffer.read().split()
    N = int(data[0]); Tmax = int(data[1]); idx = 2
    p = [0]*N; s = [0]*N                       # p:獎勵  s:服務時間
    for i in range(N):
        p[i] = int(data[idx]); s[i] = int(data[idx+1]); idx += 2
    t = [None]*N                               # t:行駛時間矩陣（可非對稱，0=無路）
    for i in range(N):
        base = idx + i*N
        t[i] = [int(x) for x in data[base:base+N]]
    del data                                   # 釋放原始大字串列表
    INF = 1 << 62

    # 路徑以鏈結串列表示：succ[i]=後繼、pred[i]=前驅；0 為倉庫(起終點)
    succ = [0]*N; pred = [0]*N
    served = bytearray(N); served[0] = 1       # 是否已納入路徑
    # 對每個未服務客戶 k，維護目前最便宜插入成本 bd[k] 與插入位置左端 left[k]
    bd = [INF]*N; left = [-1]*N

    # 計算把客戶 k 插入現有路徑各邊後，增加時間最小者（含可行性檢查：邊須為實路）
    def recompute(k):
        best = INF; bl = -1; a = 0; sk = s[k]; tk = t[k]
        while True:
            b = succ[a]; ta = t[a]; tak = ta[k]
            if tak:                            # a->k 須為實路
                tkb = tk[b]
                if tkb or k == b:              # k->b 須為實路
                    d = tak + sk + tkb - ta[b] # Δ＝新增兩邊 + 服務 − 被拆掉的舊邊
                    if d < best: best = d; bl = a
            a = b
            if a == 0: break
        bd[k] = best; left[k] = bl

    # -------- 貪婪建構：選擇程序 + 可行性檢查 + 解答檢查 --------
    def greedy_fill(cur):
        active = [k for k in range(1, N) if not served[k]]
        for k in active: recompute(k)
        while active:                          # 解答檢查：還有客戶可選就繼續
            # 選擇程序：挑「單位成本最大價值」者；Δ<=0(免費/省時)者最優先。
            # 比值以交叉相乘比較，避免浮點、支援超大整數：p_k/Δ_k > p_sel/Δ_sel
            sel = -1; bnum = 0; bden = 0; infr = -1; sinf = False
            for k in active:
                d = bd[k]
                if d >= INF or cur + d > Tmax:  # 可行性檢查：要有實路、且不超時
                    continue
                pk = p[k]
                if d <= 0:                     # 不花時間還能拿獎勵 → 最優先
                    if pk > infr: infr = pk; sel = k; sinf = True
                    continue
                if sinf: continue
                if bden == 0 or pk*bden > bnum*d or (pk*bden == bnum*d and pk > bnum):
                    bnum = pk; bden = d; sel = k
            if sel < 0: break                  # 沒有可行客戶 → 解答檢查通過，得解
            # 把 sel 插入 left[sel] 之後
            a = left[sel]; b = succ[a]
            succ[a] = sel; succ[sel] = b; pred[sel] = a; pred[b] = sel
            cur += bd[sel]; served[sel] = 1; active.remove(sel)
            # 增量更新：只重算受影響者，避免每步重掃全圖（保持高效率）
            m = sel; tm = t[m]; ta = t[a]; tam = ta[m]; tmb = tm[b]
            for k in active:
                if left[k] == a:               # 舊邊(a,b)被拆 → 重算
                    recompute(k)
                else:                          # 其餘只需檢查兩條新邊(a,m)、(m,b)
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

    # -------- 貪婪式區域改善：Or-opt(1/2/3) 整段搬移 --------
    # 把連續 L 個客戶整段(不反轉)搬到更省時的位置，騰出時間再貪婪填入更多客戶。
    # 不反轉 → 內部邊不變；只換 3 條邊，且每條都做可行性檢查，路徑恆合法。
    def oropt_pass(cur, L):
        improved = False; h = succ[0]
        while h != 0:
            tail = h; ok = True
            for _ in range(L-1):
                tail = succ[tail]
                if tail == 0: ok = False; break
            if not ok: break
            nxt_after = succ[tail]
            pv = pred[h]; nv = succ[tail]
            bridge = t[pv][nv]                  # 拆段後的橋接邊 pv->nv 須為實路
            if bridge or pv == nv:
                saved = t[pv][h] + t[tail][nv] - bridge
                if saved > 0:                  # 此段目前較浪費時間才值得搬
                    best_gain = 0; ba = -1; a = 0; t_tail = t[tail]
                    while True:
                        b = succ[a]
                        inside = False; x = h   # a,b 不可落在段內或原位
                        while True:
                            if a == x or b == x: inside = True; break
                            if x == tail: break
                            x = succ[x]
                        if not (inside or (a == pv and b == nv)):
                            ta = t[a]; tah = ta[h]
                            if tah:             # 新邊 a->段頭 須為實路
                                ttb = t_tail[b]
                                if ttb:         # 新邊 段尾->b 須為實路
                                    gain = saved - (tah + ttb - ta[b])
                                    if gain > best_gain: best_gain = gain; ba = a
                        a = b
                        if a == 0: break
                    if ba >= 0:                 # 找到更省時位置 → 搬移
                        succ[pv] = nv; pred[nv] = pv
                        bb = succ[ba]
                        succ[ba] = h; pred[h] = ba
                        succ[tail] = bb; pred[bb] = tail
                        cur -= best_gain; improved = True
            h = nxt_after
        return cur, improved

    # 主流程：先貪婪建構，再「搬移 + 再填入」迭代到收斂（自然終止，故只需 import sys）
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

    # 由鏈結串列還原路徑並輸出（以 sys.stdout.write 取代 print，降低 I/O 成本）
    route = [0]; a = succ[0]
    while a != 0: route.append(a); a = succ[a]
    route.append(0)
    total = 0
    for n in route: total += p[n]
    w = sys.stdout.write
    w(str(total)); w("\n"); w(" ".join(map(str, route))); w("\n")

main()
