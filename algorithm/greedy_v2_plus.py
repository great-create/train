import sys, time

START = time.time()
TIME_BUDGET = 5.0   # 牆鐘秒數上限（限制 8/10s，預留 I/O、啟動與慢機餘裕）


def main():
    data = sys.stdin.buffer.read().split()
    pos = 0
    N = int(data[pos]); pos += 1
    T_max = int(data[pos]); pos += 1
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

    def exact_time(route):
        t = 0
        for k in range(len(route) - 1):
            a = route[k]; b = route[k + 1]
            t += rows[a][b]
            if b != 0:
                t += s[b]
        return t

    # ---------- 階段一：比值貪婪建構（只走存在的邊，必為合法） ----------
    visited = bytearray(N)
    visited[0] = 1
    cur = 0
    tu = 0
    route = [0]
    while True:
        row = rows[cur]; rem = T_max - tu
        bj = -1; bp = 0; bc = 1
        for j in range(1, N):
            if visited[j]:
                continue
            tij = row[j]
            if tij == 0:
                continue
            bk = back[j]
            if bk == 0:
                continue
            cost = tij + s[j]
            if cost + bk > rem:
                continue
            pj = p[j]
            if bj == -1 or pj * bc > bp * cost:
                bj = j; bp = pj; bc = cost
        if bj == -1:
            break
        tu += row[bj] + s[bj]
        visited[bj] = 1
        route.append(bj)
        cur = bj
    route.append(0)

    # ---------- 改良：貪婪插入 + 移除最低 CP 值節點再重填 ----------
    def fill(route, visited, time_used):
        improved = True
        while improved:
            improved = False
            L = len(route); best = None
            for j in range(1, N):
                if visited[j]:
                    continue
                pj = p[j]; sj = s[j]
                for k in range(L - 1):
                    a = route[k]; b = route[k + 1]
                    aj = rows[a][j]
                    if aj == 0:
                        continue
                    jb = rows[j][b]
                    if jb == 0 and j != b:
                        continue
                    extra = aj + sj + jb - rows[a][b]
                    if time_used + extra > T_max:
                        continue
                    den = extra if extra > 0 else 1
                    if best is None or pj * best[1] > best[0] * den:
                        best = (pj, den, j, k, extra)
            if best is not None:
                pj, den, j, k, extra = best
                route.insert(k + 1, j); visited[j] = 1
                time_used += extra; improved = True
        return time_used

    tu = fill(route, visited, exact_time(route))   # 以實際路徑時間為唯一基準
    best_route = route[:]
    best_val = sum(p[x] for x in route if x != 0)

    no_improve = 0
    limit_no_improve = max(60, 3 * N)
    step = 0
    L = len(route)
    while (time.time() - START < TIME_BUDGET and L > 3
           and no_improve < limit_no_improve):
        step += 1
        # 掃描可合法繞過(rows[a][b]!=0)且 CP 值最低者移除；整數交叉相乘，超大整數安全
        worst_k = -1; w_p = 1; w_den = 0
        start_k = 1 + (step % (L - 2))
        k = start_k; scanned = 0
        while scanned < L - 2:
            if k >= L - 1:
                k = 1
            a = route[k - 1]; j = route[k]; b = route[k + 1]
            if rows[a][b] != 0:
                extra = rows[a][j] + s[j] + rows[j][b] - rows[a][b]
                den = extra if extra > 0 else 1
                pj = p[j]
                if worst_k == -1 or pj * w_den < w_p * den:
                    worst_k = k; w_p = pj; w_den = den
            k += 1; scanned += 1
        if worst_k == -1:
            break
        j = route[worst_k]
        del route[worst_k]; visited[j] = 0
        tu = fill(route, visited, exact_time(route))   # 重填後重算時間，杜絕誤差累積
        v = sum(p[x] for x in route if x != 0)
        if v > best_val:
            best_val = v; best_route = route[:]; no_improve = 0
        else:
            no_improve += 1
            if v < best_val:                # 回到目前最佳解再擾動
                route = best_route[:]
                visited = bytearray(N)
                for x in route:
                    visited[x] = 1
        L = len(route)

    # 最終安全檢查：確保輸出在預算內（理論上必成立）
    if exact_time(best_route) > T_max:
        best_route = [0, 0]; best_val = 0

    out = sys.stdout
    out.write(str(best_val)); out.write("\n")
    out.write(" ".join(map(str, best_route))); out.write("\n")


main()
