import sys
import time
import random

START = time.time()
BUDGET = 6.5


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
    adj = [[(j, rows[i][j], s[j], p[j]) for j in range(1, N) if i != j and rows[i][j] != 0] for i in range(N)]

    def rtime(route):
        t = 0
        for k in range(len(route) - 1):
            t += rows[route[k]][route[k + 1]]
            if route[k + 1] != 0:
                t += s[route[k + 1]]
        return t

    def reward(route):
        return sum(p[x] for x in route if x != 0)

    # ---------- 下界：多起點貪婪 + 迭代區域搜尋（移除最差/插入最佳），給 DP 強 incumbent ----------
    def greedy_from(first):
        vis = bytearray(N); vis[0] = 1; cur = 0; tu = 0; route = [0]
        if first is not None:
            c = rows[0][first]
            if c == 0 or back[first] == 0 or c + s[first] + back[first] > T:
                return None
            tu = c + s[first]; vis[first] = 1; route.append(first); cur = first
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
            tu += row[bj] + s[bj]; vis[bj] = 1; route.append(bj); cur = bj
        return route + [0]

    best = 0; best_path = [0, 0]
    for first in [None] + list(range(1, N)):
        r = greedy_from(first)
        if r is not None and reward(r) > best:
            best = reward(r); best_path = r

    def best_insert(route, j):
        bp_ = None
        for k in range(len(route) - 1):
            a = route[k]; b = route[k + 1]
            if rows[a][j] == 0 or rows[j][b] == 0:
                continue
            add = rows[a][j] + s[j] + rows[j][b] - rows[a][b]
            if bp_ is None or add < bp_[1]:
                bp_ = (k, add)
        return bp_

    rng = random.Random(1)
    ils_deadline = START + min(1.2, BUDGET * 0.3)
    cur_route = best_path[:]
    while time.time() < ils_deadline:
        c = cur_route[:]
        for _ in range(rng.randint(1, 3)):
            if len(c) <= 2:
                break
            # 只移除「移除後旁路邊 a->b 仍存在」的節點，保持路徑合法
            cands = [idx for idx in range(1, len(c) - 1) if rows[c[idx - 1]][c[idx + 1]] != 0]
            if not cands:
                break
            del c[rng.choice(cands)]
        improved = True
        while improved:
            improved = False
            inset = set(c); t = rtime(c)
            for j in sorted((x for x in range(1, N) if x not in inset), key=lambda x: -p[x]):
                fi = best_insert(c, j)
                if fi is not None and t + fi[1] <= T:
                    c.insert(fi[0] + 1, j); t += fi[1]; improved = True; break
        rw = reward(c)
        if rw > best:
            best = rw; best_path = c[:]; cur_route = c[:]
        elif rng.random() < 0.3:
            cur_route = c[:]

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

    # ---------- Held-Karp 子集 DP：依 popcount 由小到大填表，dp[(mask,last)]=最短時間 ----------
    # 以 incumbent + 分數背包上界剪枝，避免展開不可能更優的子集
    NK = N
    cur = {1 * NK + 0: (0, 0, -1)}
    par = {1 * NK + 0: -1}
    best_key = -1; best_full_mask = 1
    while cur:
        nxt = {}
        ng = nxt.get
        for key, val in cur.items():
            tu = val[0]; rew = val[1]
            last = key % NK; mask = key // NK
            bl = back[last]
            if last != 0 and bl != 0 and tu + bl <= T and rew > best:
                best = rew; best_key = key; best_full_mask = mask
            if rew + bound(mask, tu) <= best:
                continue
            for j, c, sj, pj in adj[last]:
                if mask >> j & 1:
                    continue
                nt = tu + c + sj
                if nt > T:
                    continue
                nmask = mask | (1 << j)
                nkey = nmask * NK + j
                old = ng(nkey)
                if old is None or nt < old[0]:
                    nxt[nkey] = (nt, rew + pj, last)
        for nkey, v in nxt.items():
            par[nkey] = v[2]
        cur = nxt

    # ---------- 路徑重建（若 DP 找到比 incumbent 更佳者） ----------
    if best_key != -1:
        route = []
        mask = best_full_mask; last = best_key % NK
        while last != -1 and not (mask == 1 and last == 0):
            route.append(last)
            plast = par.get(mask * NK + last, -1)
            mask ^= (1 << last)
            last = plast
        route.append(0); route.reverse()
        best_path = route + [0]

    # ---------- 合法性安全網：保證輸出路徑合法且獎勵一致 ----------
    def is_legal(route):
        if len(route) < 2 or route[0] != 0 or route[-1] != 0:
            return False
        seen = set(); t = 0
        for k in range(len(route) - 1):
            a = route[k]; b = route[k + 1]
            if a == b or rows[a][b] == 0:
                return False
            t += rows[a][b]
            if b != 0:
                if b in seen:
                    return False
                seen.add(b); t += s[b]
        return t <= T

    if not (is_legal(best_path) and reward(best_path) == best):
        # 退回最佳合法貪婪解
        best = 0; best_path = [0, 0]
        for first in [None] + list(range(1, N)):
            r = greedy_from(first)
            if r is not None and is_legal(r) and reward(r) > best:
                best = reward(r); best_path = r

    out = sys.stdout
    out.write(str(best)); out.write("\n")
    out.write(" ".join(map(str, best_path))); out.write("\n")


main()
