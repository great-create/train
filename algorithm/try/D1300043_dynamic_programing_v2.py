import sys, random
from collections import defaultdict

def main():
    d = sys.stdin.buffer.read().split()
    N=int(d[0]); Tmax=int(d[1]); idx=2
    p=[0]*N; s=[0]*N
    for i in range(N): p[i]=int(d[idx]); s[i]=int(d[idx+1]); idx+=2
    t=[None]*N
    for i in range(N):
        b=idx+i*N; t[i]=[int(x) for x in d[b:b+N]]
    del d
    INF=1<<60; sum_all=sum(p)

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
    succ=[0]*N; pred=[0]*N; inr=bytearray(N); inr[0]=1
    def ci(k):
        bb=INF; bl=-1; a=0; tk=t[k]
        while True:
            b=succ[a]; ta=t[a]; tak=ta[k]
            if tak:
                tkb=tk[b]
                if tkb or k==b:
                    dd=tak+tkb-ta[b]
                    if dd<bb: bb=dd; bl=a
            a=b
            if a==0: break
        return bb,bl
    while True:#每便插入 成本最小point
        bestc=INF; bk=-1; ba=-1
        for k in range(1,N):
            if inr[k]: continue
            c,a=ci(k)
            if a>=0 and c<bestc: bestc=c; bk=k; ba=a
        if bk<0: break
        b=succ[ba]; succ[ba]=bk; succ[bk]=b; pred[bk]=ba; pred[b]=bk; inr[bk]=1
    def trav():
        a=0; tot=0
        while True:
            b=succ[a]; tot+=t[a][b]; a=b
            if a==0: break
        return tot
    def oropt(L):
        imp=False; h=succ[0]
        while h!=0:
            tail=h; ok=True
            for _ in range(L-1):
                tail=succ[tail]
                if tail==0: ok=False; break
            if not ok: break
            nxt=succ[tail]; pv=pred[h]; nv=succ[tail]; br=t[pv][nv]
            if br or pv==nv:
                saved=t[pv][h]+t[tail][nv]-br
                if saved>0:
                    bg=0; ba=-1; a=0; tt=t[tail]
                    while True:
                        b=succ[a]; ins=False; x=h
                        while True:
                            if a==x or b==x: ins=True; break
                            if x==tail: break
                            x=succ[x]
                        if not(ins or (a==pv and b==nv)):
                            ta=t[a]; tah=ta[h]
                            if tah:
                                ttb=tt[b]
                                if ttb:
                                    g=saved-(tah+ttb-ta[b])
                                    if g>bg: bg=g; ba=a
                        a=b
                        if a==0: break
                    if ba>=0:
                        succ[pv]=nv; pred[nv]=pv; bb=succ[ba]
                        succ[ba]=h; pred[h]=ba; succ[tail]=bb; pred[bb]=tail; imp=True
            h=nxt
        return imp
    def localmin():
        while True:
            if not(oropt(1)|oropt(2)|oropt(3)|oropt(4)): break
    localmin()
    serv_all=sum(s[1:]); need=Tmax-serv_all
    bt=trav(); bsucc=succ[:]
    random.seed(1); nodes=list(range(1,N))
    it=0
    while bt>need and N>5 and it<4000:#迭代上限
        it+=1
        for _ in range(2):
            v=random.choice(nodes); pv=pred[v]; nv=succ[v]
            if pv!=nv and not t[pv][nv]: continue
            tries=0
            while tries<8:
                a=random.choice(nodes) if random.random()<0.9 else 0
                if a==v: tries+=1; continue
                b=succ[a]
                if b==v: tries+=1; continue
                if t[a][v] and t[v][b]:
                    succ[pv]=nv; pred[nv]=pv; succ[a]=v; pred[v]=a; succ[v]=b; pred[b]=v; break
                tries+=1
        localmin()
        tt=trav()
        if tt<bt: bt=tt; bsucc=succ[:]
        else:
            succ[:]=bsucc; a=0
            while True:
                b=succ[a]; pred[b]=a; a=b
                if a==0: break
    succ[:]=bsucc; a=0
    while True:
        b=succ[a]; pred[b]=a; a=b
        if a==0: break
    total=trav()+serv_all
    def free_time(v):
        pv=pred[v]; nv=succ[v]; br=t[pv][nv]
        if not(br or pv==nv): return None
        return s[v]+t[pv][v]+t[v][nv]-br
    while total>Tmax:#不可行匙就修剪
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
    inc=[0]; a=succ[0]
    while a!=0: inc.append(a); a=succ[a]
    inc.append(0)
    best_reward=sum(p[n] for n in inc); best_path=inc

    cin=[INF]*N
    for j in range(N):
        for i in range(N):
            if i!=j and t[i][j] and t[i][j]<cin[j]: cin[j]=t[i][j]
    mine=min((t[i][j] for i in range(N) for j in range(N) if i!=j and t[i][j]), default=1)
    wsorted=sorted(cin[j]+s[j] for j in range(1,N)); Wp=[0]*(N+1)
    for m in range(1,N): Wp[m]=Wp[m-1]+wsorted[m-1]
    rsorted=sorted(p[1:],reverse=True); Rp=[0]*(N+1)
    for m in range(1,N): Rp[m]=Rp[m-1]+rsorted[m-1]
    def ub(rm, avail):
        a=avail-mine; k=0
        while k+1<N and Wp[k+1]<=a: k+=1
        u=rm+Rp[k]
        return sum_all if u>sum_all else u

    #子集 DP
    if best_reward<sum_all:
        adj=[[(j,t[i][j]) for j in range(N) if i!=j and t[i][j]] for i in range(N)]
        dp={1:{0:0}}; rewm={1:0}; par={}
        by_pc=defaultdict(list); by_pc[1].append(1)
        bend=None; cap=4000000; cnt=0; stop=False
        for pc in range(1,N+1):
            if stop: break
            for mask in by_pc[pc]:
                nd=dp.get(mask)
                if nd is None: continue
                rm=rewm[mask]
                if ub(rm,Tmax)<=best_reward: continue
                for i,ti in nd.items():
                    cnt+=1
                    if cnt>cap: stop=True; break#退目前最佳
                    if i and t[i][0] and ti+t[i][0]<=Tmax and rm>best_reward:
                        best_reward=rm; bend=(mask,i)
                    if ub(rm,Tmax-ti)<=best_reward: continue
                    for j,e in adj[i]:
                        if (mask>>j)&1: continue
                        nt=ti+e+s[j]
                        if nt+dist[j]>Tmax: continue
                        nr=rm+p[j]
                        if ub(nr,Tmax-nt)<=best_reward: continue
                        nmask=mask|(1<<j); d2=dp.get(nmask)
                        if d2 is None:
                            dp[nmask]={j:nt}; rewm[nmask]=nr; by_pc[pc+1].append(nmask); par[(nmask,j)]=(mask,i)
                        elif j not in d2 or nt<d2[j]:
                            d2[j]=nt; par[(nmask,j)]=(mask,i)
                if stop: break
        if bend is not None:
            mask,i=bend; rev=[0]
            while not(mask==1 and i==0):
                rev.append(i); mask,i=par[(mask,i)]
            rev.append(0); best_path=rev[::-1]

    w=sys.stdout.write
    if best_reward<=0: w("0\n0 0\n")
    else: w(str(best_reward)); w("\n"); w(" ".join(map(str,best_path))); w("\n")

main()
