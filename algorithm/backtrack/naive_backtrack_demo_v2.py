import sys
def main():
    data=sys.stdin.buffer.read().split(); pos=0
    N=int(data[pos]); pos+=1; T=int(data[pos]); pos+=1
    p=[0]*N; s=[0]*N
    for i in range(N): p[i]=int(data[pos]); s[i]=int(data[pos+1]); pos+=2
    rows=[None]*N
    for i in range(N): rows[i]=[int(x) for x in data[pos+i*N:pos+i*N+N]]
    pos+=N*N; del data
    back=[rows[i][0] for i in range(N)]
    foot=[1<<62]*N
    for j in range(1,N):
        m=None
        for i in range(N):
            if i!=j:
                c=rows[i][j]
                if c!=0 and (m is None or c<m): m=c
        if m is not None: foot[j]=m+s[j]
    min_back=min((back[j] for j in range(1,N) if back[j]!=0),default=0)
    order=sorted(range(1,N),key=lambda j:-p[j]); M=len(order)
    of=[foot[j] for j in order]; op=[p[j] for j in order]
    adj=[[(j,rows[i][j],s[j],p[j]) for j in order if rows[i][j]!=0] for i in range(N)]
    # greedy seed
    best=0;bpath=[0,0]; v0=bytearray(N); v0[0]=1; cur=0;tu=0;rew=0;route=[0]
    while True:
        row=rows[cur];bj=-1;bp=0;bc=1;rem=T-tu
        for j in range(1,N):
            if v0[j]:continue
            c=row[j]
            if c==0:continue
            bk=back[j]
            if bk==0:continue
            cost=c+s[j]
            if cost+bk>rem:continue
            if bj==-1 or p[j]*bc>bp*cost: bj=j;bp=p[j];bc=cost
        if bj==-1:break
        tu+=row[bj]+s[bj];rew+=p[bj];v0[bj]=1;route.append(bj);cur=bj
    if rew>best: best=rew;bpath=route+[0]
    path=[0]; bb=[best,bpath]
    def dfs(cur,mask,tu,reward):
        bc=back[cur]
        if cur!=0 and bc!=0 and tu+bc<=T and reward>bb[0]:
            bb[0]=reward; bb[1]=path+[0]
        cap=T-tu-min_back; b=0
        if cap>=0:
            k=0
            while k<M:
                if not (mask>>order[k]&1):
                    f=of[k]
                    if f<=cap: b+=op[k];cap-=f
                    else: b+=op[k]*cap//f; break
                k+=1
        if reward+b<=bb[0]: return
        for j,c,sj,pj in adj[cur]:
            if mask>>j&1: continue
            nt=tu+c+sj
            if nt>T: continue
            path.append(j); dfs(j,mask|(1<<j),nt,reward+pj); path.pop()
    dfs(0,1,0,0)
    sys.stdout.write(str(bb[0])+"\n"+" ".join(map(str,bb[1]))+"\n")
main()
