import sys, heapq


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

    # dist_to_depot[j]：就是j 回去 的最短距離
    dist=[INF]*N; dist[0]=0; fin=bytearray(N)
    for _ in range(N):
        u=-1; bd=INF
        for v in range(N):
            if not fin[v] and dist[v]<bd: bd=dist[v]; u=v
        if u<0: break
        fin[u]=1
        for v in range(N):
            w=t[v][u]
            if w and bd+w<dist[v]: dist[v]=bd+w

    # 上界：每多訪 1 客戶至少花 最少邊 + 最少
    pe=[t[i][j] for i in range(N) for j in range(N) if i!=j and t[i][j]]
    mine=min(pe) if pe else 1
    mins=min((s[j] for j in range(1,N)), default=0)
    step=mine+mins if mine+mins>0 else 1
    maxp=max(p) if p else 0

    def upper_bound(tused, rew):
        avail=Tmax-tused-mine
        kmax=avail//step if avail>0 else 0
        return rew+kmax*maxp

    best_reward=0; best_path=[0,0]

    #貪婪剛凱使下界
    seen=bytearray(N); seen[0]=1; cur=0; tu=0; rew=0; gp=[0]
    while True:
        bj=-1; bn=0; bden=0; tc=t[cur]
        for j in range(N):
            if seen[j] or not tc[j]: continue
            nt=tu+tc[j]+s[j]
            if nt+dist[j]>Tmax: continue
            dt=tc[j]+s[j]
            if bj<0 or p[j]*bden>bn*dt: bj=j; bn=p[j]; bden=dt
        if bj<0: break
        seen[bj]=1; tu+=tc[bj]+s[bj]; rew+=p[bj]; cur=bj; gp.append(bj)
    if cur!=0 and t[cur][0] and tu+t[cur][0]<=Tmax:
        best_reward=rew; best_path=gp+[0]

    #(bound,序號,頂點,mask,時間,獎勵,路徑tuple)
    start_mask=1# 訪問過 {0}
    pq=[(-upper_bound(0,0), 0, 0, start_mask, 0, 0, (0,))]
    seq=1
    best_time={}#最短達時間

    while pq:
        nb, _, v, mask, tu, rew, path = heapq.heappop(pq)
        bound=-nb
        #提前stop：頂端上界都 <= 最佳 → no更好，證明最佳，結束
        if bound<=best_reward: break
        # 合法回 即為完整解
        if v!=0:
            back=t[v][0]
            if back and tu+back<=Tmax and rew>best_reward:
                best_reward=rew; best_path=list(path)+[0]
        #展開每個可達、可行、未訪的客戶
        tc=t[v]
        for j in range(N):
            if (mask>>j)&1: continue
            e=tc[j]
            if not e: continue
            nt=tu+e+s[j]
            if nt+dist[j]>Tmax: continue
            nrew=rew+p[j]
            ub=upper_bound(nt, nrew)
            if ub<=best_reward: continue#界限剪枝
            nmask=mask|(1<<j)
            key=(j,nmask)#剪枝
            pt=best_time.get(key)
            if pt is not None and pt<=nt: continue
            best_time[key]=nt
            heapq.heappush(pq,(-ub, seq, j, nmask, nt, nrew, path+(j,)))
            seq+=1

    w=sys.stdout.write
    if best_reward<=0: w("0\n0 0\n")
    else: w(str(best_reward)); w("\n"); w(" ".join(map(str,best_path))); w("\n")

main()
