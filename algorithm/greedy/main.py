#!/usr/bin/env python3
import sys
import time

def main():
data = sys.stdin.buffer.read().split()
if not data:
return

try:
    it = iter(data)
    n = int(next(it))
    t_max = int(next(it))

    p = [0] * n
    s = [0] * n
    for i in range(n):
        p[i] = int(next(it))
        s[i] = int(next(it))

    t = []
    for _ in range(n):
        t.append([int(next(it)) for _ in range(n)])
except Exception:
    sys.stdout.write("0\n0 0")
    return

if n <= 1:
    sys.stdout.write("0\n0 0")
    return

start_time = time.perf_counter()
time_limit = 7.2

best_profit = 0
best_path = [0, 0]

def route_profit(path):
    total = 0
    for v in path:
        if v:
            total += p[v]
    return total

def route_time(path):
    total = 0
    for i in range(len(path) - 1):
        a = path[i]
        b = path[i + 1]
        if a != b and t[a][b] == 0:
            return None
        total += t[a][b]
        if b:
            total += s[b]
    return total

def update(path, value=None):
    nonlocal best_profit, best_path
    if len(path) <= 2:
        return
    if value is None:
        value = route_profit(path)
    if value > best_profit or (value == best_profit and len(path) > len(best_path)):
        rt = route_time(path)
        if rt is not None and rt <= t_max:
            best_profit = value
            best_path = path[:]

def append_greedy(mode):
    visited = [False] * n
    visited[0] = True
    path = [0]
    cur = 0
    used = 0
    value = 0

    while True:
        best = -1
        best_key = None
        row = t[cur]

        for v in range(1, n):
            if visited[v]:
                continue

            go = row[v]
            back = t[v][0]
            if go == 0 or back == 0:
                continue

            add = go + s[v]
            if used + add + back > t_max:
                continue

            pv = p[v]
            if mode == 0:
                key = (add, -pv, v)
            elif mode == 1:
                key = (-pv, add, v)
            elif mode == 2:
                key = (-(pv * 1000000 // add), add, v)
            elif mode == 3:
                key = (-(pv * 1000000 // (add + back)), add + back, v)
            elif mode == 4:
                key = (-(pv * 1000000 // max(1, go + s[v] + back)), -pv, v)
            else:
                key = (-(pv - add), add, v)

            if best_key is None or key < best_key:
                best_key = key
                best = v

        if best < 0:
            break

        visited[best] = True
        path.append(best)
        used += t[cur][best] + s[best]
        value += p[best]
        cur = best

    if len(path) > 1 and t[cur][0] != 0 and used + t[cur][0] <= t_max:
        path.append(0)
        update(path, value)

def insertion_greedy(mode):
    path = [0, 0]
    used = 0
    value = 0
    visited = [False] * n
    visited[0] = True

    while True:
        best = -1
        best_pos = -1
        best_extra = 0
        best_key = None

        for v in range(1, n):
            if visited[v]:
                continue

            sv = s[v]
            pv = p[v]

            for pos in range(len(path) - 1):
                a = path[pos]
                b = path[pos + 1]

                av = t[a][v]
                vb = t[v][b]

                if av == 0 or vb == 0:
                    continue

                old = t[a][b] if a != b else 0
                if a != b and old == 0:
                    continue

                extra = av + sv + vb - old
                if extra < 0:
                    extra = av + sv + vb

                if used + extra > t_max:
                    continue

                if mode == 0:
                    key = (extra, -pv, pos, v)
                elif mode == 1:
                    key = (-(pv * 1000000 // max(1, extra)), extra, pos, v)
                elif mode == 2:
                    key = (-pv, extra, pos, v)
                else:
                    key = (-(pv - extra), extra, pos, v)

                if best_key is None or key < best_key:
                    best_key = key
                    best = v
                    best_pos = pos + 1
                    best_extra = extra

        if best < 0:
            break

        path.insert(best_pos, best)
        visited[best] = True
        used += best_extra
        value += p[best]

    update(path, value)

for m in range(6):
    append_greedy(m)

for m in range(4):
    insertion_greedy(m)

if n <= 22:
    nodes = []
    for i in range(1, n):
        if t[0][i] and t[i][0] and t[0][i] + s[i] + t[i][0] <= t_max:
            nodes.append(i)

    nodes.sort(key=lambda x: (-p[x], s[x] + t[0][x] + t[x][0], x))

    if len(nodes) <= 20:
        m = len(nodes)
        idx = {nodes[i]: i for i in range(m)}
        suffix = [0] * (m + 1)
        for i in range(m - 1, -1, -1):
            suffix[i] = suffix[i + 1] + p[nodes[i]]

        visited = [False] * n
        visited[0] = True
        cur_path = [0]

        sys.setrecursionlimit(1000000)

        def dfs(cur, used, value, start_idx):
            if time.perf_counter() - start_time > time_limit:
                return

            if t[cur][0] and used + t[cur][0] <= t_max:
                update(cur_path + [0], value)

            if start_idx < m and value + suffix[start_idx] < best_profit:
                return

            row = t[cur]
            cand = []
            for k in range(start_idx, m):
                v = nodes[k]
                if visited[v]:
                    continue
                go = row[v]
                back = t[v][0]
                if go == 0 or back == 0:
                    continue
                add = go + s[v]
                if used + add + back <= t_max:
                    cand.append((-(p[v] * 1000000 // max(1, add + back)), add, k, v))

            cand.sort()

            for _, add, k, v in cand:
                visited[v] = True
                cur_path.append(v)
                dfs(v, used + add, value + p[v], k + 1)
                cur_path.pop()
                visited[v] = False

        dfs(0, 0, 0, 0)

if best_profit <= 0:
    sys.stdout.write("0\n0 0")
else:
    sys.stdout.write(str(best_profit) + "\n" + " ".join(map(str, best_path)))

if name == "main":
main()
