import sys
# usage: python3 verify.py D0000000.in < program_output
def main():
    infile=sys.argv[1]
    d=open(infile,'rb').read().split(); N=int(d[0]); T=int(d[1]); pos=2
    p=[0]*N; s=[0]*N
    for i in range(N): p[i]=int(d[pos]); s[i]=int(d[pos+1]); pos+=2
    rows=[[int(x) for x in d[pos+i*N:pos+i*N+N]] for i in range(N)]
    out=sys.stdin.read().split('\n')
    decl=int(out[0].strip())
    route=list(map(int, out[1].split()))
    seen=set(); t=0; ok=True; why=""
    if route[0]!=0 or route[-1]!=0: ok=False; why="頭尾非倉庫0"
    for k in range(len(route)-1):
        a,b=route[k],route[k+1]
        if a==b: ok=False; why="連續重複"
        if rows[a][b]==0: ok=False; why="走不存在的邊 %d->%d"%(a,b)
        t+=rows[a][b]
        if b!=0:
            if b in seen: ok=False; why="重複拜訪 %d"%b
            seen.add(b); t+=s[b]
    actual=sum(p[x] for x in route if x!=0)
    if t>T: ok=False; why="超過時間 %d>%d"%(t,T)
    if decl!=actual: ok=False; why="宣告獎勵%d≠實際%d"%(decl,actual)
    print("合法:%s 宣告獎勵:%d 實際:%d 路徑時間:%d/%d 走訪:%d/%d 最佳解(sum_p=%d):%s %s"%(
        ok,decl,actual,t,T,len(seen),N-1,sum(p), decl==sum(p), ("" if ok else "← "+why)))
main()
