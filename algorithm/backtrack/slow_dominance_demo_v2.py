import sys
def main():
    first=input().split(); N=int(first[0]); T=int(first[1])
    p=[0]*N; s=[0]*N
    for i in range(N):
        a,b=input().split(); p[i]=int(a); s[i]=int(b)
    rows=[list(map(int,input().split())) for _ in range(N)]
    back=[rows[i][0] for i in range(N)]
    best=[0]; bpath=[[0,0]]; path=[0]; memo={}
    def dfs(cur,mask,tu,reward):
        bc=back[cur]
        if cur!=0 and bc!=0 and tu+bc<=T and reward>best[0]:
            best[0]=reward; bpath[0]=path+[0]
        # sloppy bound: 每次重新排序未訪節點做分數背包
        unv=[j for j in range(1,N) if not (mask>>j&1)]
        unv.sort(key=lambda j:-p[j])
        cap=T-tu; b=0
        for j in unv:
            f=999999
            for i in range(N):
                if i!=j and rows[i][j]!=0 and rows[i][j]<f: f=rows[i][j]
            f+=s[j]
            if f<=cap: b+=p[j]; cap-=f
            else: b+=p[j]*cap//f; break
        if reward+b<=best[0]: return
        for j in range(1,N):           # 無鄰接表，逐一判 0
            if mask>>j&1: continue
            c=rows[cur][j]
            if c==0: continue
            nt=tu+c+s[j]
            if nt>T: continue
            key=(mask|(1<<j), j)        # tuple 鍵
            pv=memo.get(key)
            if pv is not None and pv<=nt: continue
            memo[key]=nt
            path.append(j); dfs(j,mask|(1<<j),nt,reward+p[j]); path.pop()
    dfs(0,1,0,0)
    print(best[0]); print(" ".join(map(str,bpath[0])))
main()
