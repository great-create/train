import sys

# ============================================================================
# 限時獎勵收集配送 — 回溯法 (Backtracking)，僅用標準輸入/輸出 import sys
# 對應講義「選擇程序 / 可行性檢查 / 解答檢查」+ 回溯法「嘗試→遞迴→還原」與剪枝。
# 小測資(N 小)可窮舉得到確切最佳解；大測資以節點上限保護並退回啟發式下界。
# ============================================================================

def main():
    d = sys.stdin.buffer.read().split()
    N=int(d[0]); Tmax=int(d[1]); idx=2
    p=[0]*N; s=[0]*N
    for i in range(N): p[i]=int(d[idx]); s[i]=int(d[idx+1]); idx+=2
    t=[None]*N
    for i in range(N):
        b=idx+i*N; t[i]=[int(x) for x in d[b:b+N]]
    del d
    INF=1<<60

    # dist_to_depot[j] = j 回倉庫 0 的最短距離（反向圖上的 Dijkstra，陣列版 O(N^2)，免 heapq）
    # 作為「之後仍能回倉庫」的可採納下界，剪枝不會誤刪可行解。
    dist=[INF]*N; dist[0]=0; done=bytearray(N)
    for _ in range(N):
        u=-1; bd=INF
        for v in range(N):
            if not done[v] and dist[v]<bd: bd=dist[v]; u=v
        if u<0: break
        done[u]=1
        for v in range(N):                 # 反向：邊 v->u 存在則 dist[v] 可由 dist[u] 更新
            w=t[v][u]
            if w and bd+w<dist[v]: dist[v]=bd+w

    best_reward=[0]; best_path=[[0,0]]

    # ---- 先用貪婪求初始下界（加速上界剪枝）----
    served=bytearray(N); served[0]=1
    cur=0; tused=0; rew=0; gp=[0]
    while True:
        bj=-1; bn=0; bden=0; tc=t[cur]
        for j in range(N):
            if served[j]: continue
            e=tc[j]
            if not e: continue
            nt=tused+e+s[j]
            if nt+dist[j]>Tmax: continue
            dt=e+s[j]
            if bj<0 or p[j]*bden>bn*dt:     # 獎勵/增加時間 最大者
                bj=j; bn=p[j]; bden=dt
        if bj<0: break
        served[bj]=1; tused+=tc[bj]+s[bj]; rew+=p[bj]; cur=bj; gp.append(bj)
    if cur!=0 and t[cur][0] and tused+t[cur][0]<=Tmax:
        best_reward[0]=rew; best_path[0]=gp+[0]

    # 每次延伸至少花「最便宜的邊 + 最小服務時間」，用於估「最多還能服務幾個客戶」
    posedges=[t[i][j] for i in range(N) for j in range(N) if i!=j and t[i][j]]
    mine=min(posedges) if posedges else 1
    mins=min((s[j] for j in range(1,N)), default=0)
    step=mine+mins if mine+mins>0 else 1
    maxp=max(p) if p else 0

    # ---- 回溯法 DFS ----
    visited=bytearray(N); visited[0]=1
    path=[0]
    NODECAP=2000000                 # 節點上限安全網（取代時間限制；小測資遠不會用到）
    cnt=[0]
    sys.setrecursionlimit(10000)

    def dfs(cur, tused, rew):
        # 解答檢查：能合法回倉庫就是一個完整解
        if cur!=0:
            back=t[cur][0]
            if back and tused+back<=Tmax and rew>best_reward[0]:
                best_reward[0]=rew; best_path[0]=path+[0]
        cnt[0]+=1
        if cnt[0]>NODECAP: return
        # 上界剪枝(O(1) 可採納)：再訪 k 個客戶並返回，至少花 k*step + mine
        avail=Tmax-tused-mine
        kmax=avail//step if avail>0 else 0
        if rew+kmax*maxp<=best_reward[0]: return
        tc=t[cur]
        # 選擇程序：依獎勵大者優先嘗試
        cand=[]
        for j in range(N):
            if visited[j]: continue
            e=tc[j]
            if not e: continue                  # 可行性檢查：須為實路
            nt=tused+e+s[j]
            if nt+dist[j]>Tmax: continue        # 可行性檢查：延伸後仍能回倉庫
            cand.append((p[j],j,nt))
        cand.sort(reverse=True)
        for pj,j,nt in cand:
            visited[j]=1; path.append(j)
            dfs(j, nt, rew+pj)                  # 遞迴
            path.pop(); visited[j]=0            # 還原(undo)

    dfs(0,0,0)

    w=sys.stdout.write
    if best_reward[0]<=0:
        w("0\n0 0\n")
    else:
        w(str(best_reward[0])); w("\n"); w(" ".join(map(str,best_path[0]))); w("\n")

main()
