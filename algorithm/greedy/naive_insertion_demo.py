import sys
def main():
    d=sys.stdin.read().split(); idx=0
    N=int(d[idx]); idx+=1; T=int(d[idx]); idx+=1
    p=[0]*N; s=[0]*N
    for i in range(N):
        p[i]=int(d[idx]); idx+=1; s[i]=int(d[idx]); idx+=1
    t=[[int(d[idx+i*N+j]) for j in range(N)] for i in range(N)]; idx+=N*N
    route=[0,0]; vis=[False]*N; vis[0]=True
    def used():
        tot=0
        for k in range(len(route)-1):
            tot+=t[route[k]][route[k+1]]
            if route[k+1]!=0: tot+=s[route[k+1]]
        return tot
    while True:
        best=None
        for j in range(1,N):
            if vis[j]: continue
            for k in range(len(route)-1):
                a=route[k]; b=route[k+1]
                if a!=j and t[a][j]==0: continue
                if j!=b and t[j][b]==0: continue
                cand=route[:k+1]+[j]+route[k+1:]
                # naive: recompute whole route time each trial (O(N) each)
                tot=0; okk=True
                for x in range(len(cand)-1):
                    e=t[cand[x]][cand[x+1]]
                    if x>0 and e==0 and cand[x]!=cand[x+1]: okk=False; break
                    tot+=e
                    if cand[x+1]!=0: tot+=s[cand[x+1]]
                if not okk or tot>T: continue
                ratio=p[j]/ (tot-used()+1)
                if best is None or ratio>best[0]:
                    best=(ratio,j,k)
        if best is None: break
        _,j,k=best; route=route[:k+1]+[j]+route[k+1:]; vis[j]=True
    print(sum(p[x] for x in route if x!=0))
    print(" ".join(map(str,route)))
main()
