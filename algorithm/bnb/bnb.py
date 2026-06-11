import sys
import heapq


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
        # 上界 = 扣必要回倉後，依獎勵大→小、僅未訪節點做分數背包（樂觀剩餘可得獎勵）
        cap = T - time_used - min_back
        if cap < 0:
            return 0
        b = 0
        k = 0
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

    # ---------- 多起點比值貪婪：強下界（incumbent） ----------
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

    # ---------- 最佳優先 branch and bound（優先佇列依上界由大到小展開） ----------
    memo = {}                       # (mask,last) -> 最短到達時間（支配剪枝）
    cnt = 0
    # heap 元素：(-上界, 序號, cur, mask, time_used, reward, path)
    start_bound = bound(1, 0)
    heap = [(-start_bound, 0, 0, 1, 0, 0, (0,))]
    while heap:
        neg_b, _, cur, mask, tu, reward, path = heapq.heappop(heap)
        if -neg_b <= best:          # 佇列中最高上界已不可能超越 incumbent → 全域最佳已確定
            break
        row_adj = adj[cur]
        for j, c, sj, pj in row_adj:
            if mask >> j & 1:
                continue
            nt = tu + c + sj
            if nt > T:
                continue
            nmask = mask | (1 << j)
            key = nmask * N + j
            pv = memo.get(key)
            if pv is not None and pv <= nt:
                continue
            memo[key] = nt
            nr = reward + pj
            npath = path + (j,)
            bj = back[j]
            if bj != 0 and nt + bj <= T and nr > best:   # 可在此收尾 → 更新 incumbent
                best = nr
                best_path = list(npath) + [0]
            ub = nr + bound(nmask, nt)
            if ub > best:                                # 仍有希望超越 → 入列
                cnt += 1
                heapq.heappush(heap, (-ub, cnt, j, nmask, nt, nr, npath))

    out = sys.stdout
    out.write(str(best)); out.write("\n")
    out.write(" ".join(map(str, best_path))); out.write("\n")


main()
