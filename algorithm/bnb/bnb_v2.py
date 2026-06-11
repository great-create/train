import sys
from heapq import heappush, heappop


def main():
    data = sys.stdin.buffer.read().split()
    pos = 0
    N = int(data[pos]); pos += 1
    T = int(data[pos]); pos += 1
    p = [0] * N
    s = [0] * N
    for i in range(N):
        p[i] = int(data[pos]); pos += 1
        s[i] = int(data[pos]); pos += 1
    rows = [None] * N
    for i in range(N):
        base = pos + i * N
        rows[i] = [int(x) for x in data[base:base + N]]
    pos += N * N
    del data

    back = [rows[i][0] for i in range(N)]
    foot = [1 << 62] * N
    for j in range(1, N):
        m = None
        for i in range(N):
            if i != j:
                c = rows[i][j]
                if c != 0 and (m is None or c < m):
                    m = c
        if m is not None:
            foot[j] = m + s[j]
    min_back = min((back[j] for j in range(1, N) if back[j] != 0), default=0)

    order = sorted(range(1, N), key=lambda j: -p[j]); M = len(order)
    of = [foot[j] for j in order]
    op = [p[j] for j in order]
    adj = [[(j, rows[i][j], s[j], p[j]) for j in order if rows[i][j] != 0] for i in range(N)]

    def bound(mask, time_used):
        cap = T - time_used - min_back
        if cap < 0:
            return 0
        b = 0; k = 0
        while k < M:
            if not (mask >> order[k] & 1):
                f = of[k]
                if f <= cap:
                    b += op[k]; cap -= f
                else:
                    b += op[k] * cap // f
                    break
            k += 1
        return b

    # ---------- 多起點比值貪婪：強 incumbent ----------
    def greedy_from(first):
        vis = bytearray(N); vis[0] = 1; cur = 0; tu = 0; rew = 0; route = [0]
        if first is not None:
            c = rows[0][first]
            if c == 0 or back[first] == 0 or c + s[first] + back[first] > T:
                return 0, None
            tu = c + s[first]; rew = p[first]; vis[first] = 1; route.append(first); cur = first
        while True:
            row = rows[cur]; bj = -1; bp = 0; bc = 1; rem = T - tu
            for j in range(1, N):
                if vis[j]:
                    continue
                c = row[j]
                if c == 0:
                    continue
                bk = back[j]
                if bk == 0:
                    continue
                cost = c + s[j]
                if cost + bk > rem:
                    continue
                if bj == -1 or p[j] * bc > bp * cost:
                    bj = j; bp = p[j]; bc = cost
            if bj == -1:
                break
            tu += row[bj] + s[bj]; rew += p[bj]; vis[bj] = 1; route.append(bj); cur = bj
        return rew, route + [0]

    best = 0; best_path = [0, 0]
    for first in [None] + list(range(1, N)):
        r, rt = greedy_from(first)
        if rt is not None and r > best:
            best = r; best_path = rt

    # ---------- 最佳優先 branch and bound ----------
    # 狀態以平行陣列存放，heap 只放 (-上界, id)；父指標重建路徑
    st_cur = [0]; st_mask = [1]; st_tu = [0]; st_par = [-1]; st_node = [0]; st_rew = [0]
    use_flat = (1 << N) * N <= 4_000_000
    BIG = 1 << 62
    memo = [BIG] * ((1 << N) * N) if use_flat else {}
    if use_flat:
        memo[0 + 0] = 0           # (mask=1<<0 ... 用 mask*N+last)；root: mask=1,last=0 -> key=1*N+0
        memo[1 * N + 0] = 0
    else:
        memo[1 * N + 0] = 0

    best_par = -1; best_last = -1
    heap = [(-bound(1, 0), 0)]
    while heap:
        neg_b, sid = heappop(heap)
        if -neg_b <= best:                       # 頂端上界已無法超越 incumbent → 證明最佳
            break
        cur = st_cur[sid]; mask = st_mask[sid]; tu = st_tu[sid]; reward = st_rew[sid]
        kcur = mask * N + cur
        if (memo[kcur] if use_flat else memo.get(kcur, BIG)) < tu:
            continue                             # 此狀態已被更短時間的同態支配 → 略過
        for j, c, sj, pj in adj[cur]:
            if mask >> j & 1:
                continue
            nt = tu + c + sj
            if nt > T:
                continue
            nmask = mask | (1 << j)
            key = nmask * N + j
            if use_flat:
                if memo[key] <= nt:
                    continue
                memo[key] = nt
            else:
                pvv = memo.get(key)
                if pvv is not None and pvv <= nt:
                    continue
                memo[key] = nt
            nr = reward + pj
            bj = back[j]
            if bj != 0 and nt + bj <= T and nr > best:
                best = nr; best_par = sid; best_last = j
            ub = nr + bound(nmask, nt)
            if ub > best:
                nid = len(st_cur)
                st_cur.append(j); st_mask.append(nmask); st_tu.append(nt)
                st_par.append(sid); st_node.append(j); st_rew.append(nr)
                heappush(heap, (-ub, nid))

    # 重建最佳路徑（父指標）
    if best_par != -1:
        nodes = []; x = best_par
        while x != -1:
            nodes.append(st_node[x]); x = st_par[x]
        nodes.reverse()                          # [0, ...]
        best_path = nodes + [best_last, 0]

    out = sys.stdout
    out.write(str(best)); out.write("\n")
    out.write(" ".join(map(str, best_path))); out.write("\n")


main()
