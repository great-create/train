import sys, time, random

# ============================================================================
# 限時獎勵收集配送（Orienteering）— 貪婪演算法
# 對應課堂講義 Class 4「The Greedy Approach」三步驟框架。
#
# 【核心洞察】全部客戶的「服務時間總和 < T_max」，瓶頸在「行駛」而非服務；
#   故策略為：以貪婪最近鄰把（幾乎）所有節點用最短行駛串成路徑，
#   服務時間自然放得下 → 服務所有人 = 收集全部獎勵 = 最佳解。
#
# 對應講義三步驟（與 Prim/Dijkstra「每次選最接近的頂點」同一精神）：
#   選擇程序 Selection Procedure：每步貪婪走到「最便宜（行駛最小）的未訪客戶」
#   可行性檢查 Feasibility Check  ：所選邊須為實路（t≠0）；最終總時間 ≤ T_max
#   解答檢查   Solution Check     ：所有節點都已串入路徑（並回到倉庫）即得解
#
# 之後以 Or-opt 區域搜尋縮短行駛；若某測資無法全服務，再貪婪修剪到預算內。
# 純標準函式庫；輸出用 sys.stdout.write；讀入後即釋放原始資料。
# ============================================================================

def main():
    st = time.time()
    d = sys.stdin.buffer.read().split()
    N=int(d[0]); Tmax=int(d[1]); idx=2
    p=[0]*N; s=[0]*N                          # p:獎勵  s:服務時間
    for i in range(N): p[i]=int(d[idx]); s[i]=int(d[idx+1]); idx+=2
    t=[None]*N                                # t:行駛矩陣（可非對稱，0=無路）
    for i in range(N):
        b=idx+i*N; t[i]=[int(x) for x in d[b:b+N]]
    del d                                     # 釋放原始大字串列表
    INF=1<<60
    # 路徑以鏈結串列表示：succ/pred；0 為倉庫(起終點)
    succ=[0]*N; pred=[0]*N; inr=bytearray(N); inr[0]=1

    # ---- (1) 最近鄰貪婪建構 ----
    #   選擇程序：站在目前節點，挑「行駛最便宜」的未訪客戶前往
    #   可行性檢查：tc[j] 必須為實路(≠0) 才可走
    cur=0; order=[0]
    while True:                               # 解答檢查（建構階段）：還能往下走就繼續
        tc=t[cur]; best=INF; bn=-1
        for j in range(N):
            if not inr[j] and tc[j] and tc[j]<best:  # 未訪 + 有實路 + 更便宜
                best=tc[j]; bn=j
        if bn<0: break                        # 無可行下一步 → 結束最近鄰串接
        inr[bn]=1; order.append(bn); cur=bn
    for i in range(len(order)-1): succ[order[i]]=order[i+1]; pred[order[i+1]]=order[i]
    succ[order[-1]]=0; pred[0]=order[-1]      # 收尾回倉庫

    # ---- (2) 最便宜插入：把最近鄰漏接的節點補進路徑 ----
    #   選擇程序：為節點 k 找「行駛增量最小」的插入邊
    #   可行性檢查：插入後左右兩條新邊(a->k, k->b)都須為實路
    def ci(k):
        best=INF; bl=-1; a=0; tk=t[k]
        while True:
            b=succ[a]; ta=t[a]; tak=ta[k]
            if tak:                           # a->k 須為實路
                tkb=tk[b]
                if tkb or k==b:               # k->b 須為實路
                    dd=tak+tkb-ta[b]
                    if dd<best: best=dd; bl=a
            a=b
            if a==0: break
        return bl
    for k in range(1,N):
        if not inr[k]:
            a=ci(k)
            if a>=0:
                b=succ[a]; succ[a]=k; succ[k]=b; pred[k]=a; pred[b]=k; inr[k]=1

    def trav():                               # 目前路徑的行駛總長
        a=0; tot=0
        while True:
            b=succ[a]; tot+=t[a][b]; a=b
            if a==0: break
        return tot

    # ---- (3) Or-opt(L) 區域搜尋：把連續 L 個客戶整段(不反轉)搬到更省行駛處 ----
    #   不反轉 → 內部邊不變；只換 3 條邊，且每條都做可行性檢查(須為實路)，路徑恆合法
    def oropt(L):
        imp=False; h=succ[0]
        while h!=0:
            tail=h; ok=True
            for _ in range(L-1):
                tail=succ[tail]
                if tail==0: ok=False; break
            if not ok: break
            nxt=succ[tail]; pv=pred[h]; nv=succ[tail]; br=t[pv][nv]
            if br or pv==nv:                  # 拆段後的橋接邊 pv->nv 須為實路
                saved=t[pv][h]+t[tail][nv]-br
                if saved>0:
                    bg=0; ba=-1; a=0; tt=t[tail]
                    while True:
                        b=succ[a]; ins=False; x=h    # a,b 不可落在段內或原位
                        while True:
                            if a==x or b==x: ins=True; break
                            if x==tail: break
                            x=succ[x]
                        if not(ins or (a==pv and b==nv)):
                            ta=t[a]; tah=ta[h]
                            if tah:           # 新邊 a->段頭 須為實路
                                ttb=tt[b]
                                if ttb:       # 新邊 段尾->b 須為實路
                                    g=saved-(tah+ttb-ta[b])
                                    if g>bg: bg=g; ba=a
                        a=b
                        if a==0: break
                    if ba>=0:
                        succ[pv]=nv; pred[nv]=pv; bb=succ[ba]
                        succ[ba]=h; pred[h]=ba; succ[tail]=bb; pred[bb]=tail; imp=True
            h=nxt
        return imp
    def localmin():                           # Or-opt 迭代到無法再縮短行駛
        while True:
            if not(oropt(1)|oropt(2)|oropt(3)|oropt(4)): break

    serv_all=sum(s[1:])
    need=Tmax-serv_all                        # 全服務所允許的最大行駛（可行性門檻）

    localmin()
    best_t=trav(); best_succ=succ[:]

    # ---- (4) 迭代局部搜尋：擾動 + 再 localmin，把行駛壓更短 ----
    #   解答檢查：一旦行駛 ≤ need 即可全服務（= 最佳解），立刻停止；否則跑到安全時限
    DEADLINE=st+4.5                           # 安全時限，留餘裕給較慢的評分機
    random.seed(1)
    nodes=list(range(1,N))
    while best_t>need and N>5 and time.time()<DEADLINE:
        for _ in range(3):                    # 擾動：隨機把幾個點搬到隨機合法位置
            v=random.choice(nodes); pv=pred[v]; nv=succ[v]
            if pv!=nv and not t[pv][nv]: continue
            tries=0
            while tries<8:
                a=random.choice(nodes) if random.random()<0.9 else 0
                if a==v: tries+=1; continue
                b=succ[a]
                if b==v: tries+=1; continue
                if t[a][v] and t[v][b]:       # 可行性檢查：兩條新邊須為實路
                    succ[pv]=nv; pred[nv]=pv
                    succ[a]=v; pred[v]=a; succ[v]=b; pred[b]=v
                    break
                tries+=1
        localmin()
        tt=trav()
        if tt<best_t:
            best_t=tt; best_succ=succ[:]
        else:                                 # 沒更短 → 回復目前最短
            succ[:]=best_succ; a=0
            while True:
                b=succ[a]; pred[b]=a; a=b
                if a==0: break

    succ[:]=best_succ; a=0
    while True:
        b=succ[a]; pred[b]=a; a=b
        if a==0: break

    # ---- (5) 修剪：若仍超預算（無法全服務），貪婪移除「省時最多/損獎勵最少」者 ----
    #   選擇程序：每次移除 key=省下時間/獎勵 最大的客戶；可行性檢查：橋接邊須為實路
    total=best_t+serv_all
    def free_time(v):
        pv=pred[v]; nv=succ[v]; br=t[pv][nv]
        if not (br or pv==nv): return None
        return s[v]+t[pv][v]+t[v][nv]-br
    while total>Tmax:                         # 解答檢查：壓到 ≤ T_max 即得可行解
        bv=-1; bk=None; v=succ[0]
        while v!=0:
            g=free_time(v)
            if g is not None and g>0:
                key=g if p[v]==0 else g/p[v]
                if bk is None or key>bk: bk=key; bv=v
            v=succ[v]
        if bv<0: break
        v=bv; pv=pred[v]; nv=succ[v]; g=free_time(v)
        succ[pv]=nv; pred[nv]=pv; total-=g

    # ---- 輸出 ----
    route=[0]; a=succ[0]
    while a!=0: route.append(a); a=succ[a]
    route.append(0)
    tot=0
    for n in route: tot+=p[n]
    w=sys.stdout.write
    w(str(tot)); w("\n"); w(" ".join(map(str,route))); w("\n")

main()
