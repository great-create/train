#!/usr/bin/env python3
import sys
import time

def main():
a = sys.stdin.buffer.read().split()
if not a:
return

q = 0
n = int(a[q])
q += 1
limit = int(a[q])
q += 1

prize = [0] * n
serv = [0] * n

for i in range(n):
    prize[i] = int(a[q])
    q += 1
    serv[i] = int(a[q])
    q += 1

mat = []
for _ in range(n):
    row = [0] * n
    for j in range(n):
        row[j] = int(a[q])
        q += 1
    mat.append(row)

if n <= 1:
    sys.stdout.write("0\n0 0\n")
    return

deadline = time.perf_counter() + 6.75
inf = 10 ** 100
nodes = list(range(1, n))

min_out = [inf] * n
min_in = [inf] * n

for i, row in enumerate(mat):
    best = inf
    for j, w in enumerate(row):
        if i != j and w:
            if w < best:
                best = w
            if w < min_in[j]:
                min_in[j] = w
    min_out[i] = best

best_value = 0
best_route = [0, 0]

def route_time(route):
    if route[0] != 0 or route[-1] != 0:
        return inf

    if len(route) == 2:
        return 0 if route[0] == 0 and route[1] == 0 else inf

    used = 0
    seen = bytearray(n)
    prev = route[0]

    for i in range(1, len(route)):
        v = route[i]

        if prev == v:
            return inf

        w = mat[prev][v]
        if w == 0:
            return inf

        used += w

        if v:
            if seen[v]:
                return inf
            seen[v] = 1
            used += serv[v]

        prev = v

    return used

def route_value(route):
    total = 0
    for v in route:
        if v:
            total += prize[v]
    return total

def save_best(route, value=None, used=None):
    nonlocal best_value, best_route

    if len(route) <= 2:
        return

    if used is None:
        used = route_time(route)

    if used > limit:
        return

    if value is None:
        value = route_value(route)

    if value > best_value or (value == best_value and value > 0 and route < best_route):
        best_value = value
        best_route = route[:]

def insert_cost(route, pos, v):
    a0 = route[pos]
    b0 = route[pos + 1]

    old = 0 if a0 == b0 else mat[a0][b0]
    if a0 != b0 and old == 0:
        return None

    av = mat[a0][v]
    vb = mat[v][b0]

    if av == 0 or vb == 0:
        return None

    return av + serv[v] + vb - old

def fill(route, used, value, mode):
    inside = bytearray(n)
    for v in route:
        inside[v] = 1

    while time.perf_counter() < deadline:
        choose = -1
        where = -1
        add_time = 0
        best_key = None
        m = len(route)

        for v in nodes:
            if inside[v]:
                continue

            pv = prize[v]
            if pv <= 0 and mode != 0:
                continue

            for pos in range(m - 1):
                extra = insert_cost(route, pos, v)

                if extra is None or used + extra > limit:
                    continue

                if mode == 0:
                    key = (extra, -pv, v, pos)
                elif mode == 1:
                    key = (-(pv * 10000019 // max(1, extra)), extra, v, pos)
                elif mode == 2:
                    key = (-pv, extra, v, pos)
                elif mode == 3:
                    key = (-(pv - extra), extra, v, pos)
                else:
                    mi = min_in[v] if min_in[v] < inf else 0
                    mo = min_out[v] if min_out[v] < inf else 0
                    key = (-(pv * 10000019 // max(1, serv[v] + mi + mo)), extra, v, pos)

                if best_key is None or key < best_key:
                    best_key = key
                    choose = v
                    where = pos + 1
                    add_time = extra

        if choose < 0:
            break

        route.insert(where, choose)
        inside[choose] = 1
        used += add_time
        value += prize[choose]
        save_best(route, value, used)

    return used, value

def shorten(route, used):
    changed = True

    while changed and time.perf_counter() < deadline:
        changed = False
        best_delta = 0
        best_move = None
        m = len(route)

        for i in range(1, m - 1):
            x = route[i]
            a0 = route[i - 1]
            b0 = route[i + 1]

            bridge = 0 if a0 == b0 else mat[a0][b0]
            if a0 != b0 and bridge == 0:
                continue

            remove_delta = bridge - mat[a0][x] - mat[x][b0] - serv[x]

            for pos in range(m - 1):
                if pos == i - 1 or pos == i:
                    continue

                c0 = route[pos]
                d0 = route[pos + 1]

                old = 0 if c0 == d0 else mat[c0][d0]
                if c0 != d0 and old == 0:
                    continue

                cx = mat[c0][x]
                xd = mat[x][d0]

                if cx == 0 or xd == 0:
                    continue

                delta = remove_delta + cx + serv[x] + xd - old

                if delta < best_delta:
                    best_delta = delta
                    best_move = (i, pos)

        if best_move is not None:
            i, pos = best_move
            x = route.pop(i)
            if pos > i:
                pos -= 1
            route.insert(pos + 1, x)
            used += best_delta
            changed = True
            continue

        m = len(route)
        window = 55 if m > 90 else m

        for i in range(1, m - 2):
            a0 = route[i - 1]
            left = route[i]
            old_left = mat[a0][left]

            if old_left == 0:
                continue

            end = m - 1
            if end > i + window:
                end = i + window

            for j in range(i + 1, end):
                right = route[j]
                b0 = route[j + 1]

                ar = mat[a0][right]
                lb = mat[left][b0]

                if ar == 0 or lb == 0:
                    continue

                old_mid = 0
                new_mid = 0
                ok = True

                for k in range(i, j):
                    old_mid += mat[route[k]][route[k + 1]]
                    rw = mat[route[k + 1]][route[k]]
                    if rw == 0:
                        ok = False
                        break
                    new_mid += rw

                if not ok:
                    continue

                delta = ar + new_mid + lb - old_left - old_mid - mat[right][b0]

                if delta < best_delta:
                    best_delta = delta
                    best_move = (i, j)

            if time.perf_counter() >= deadline:
                break

        if best_move is not None:
            i, j = best_move
            route[i:j + 1] = reversed(route[i:j + 1])
            used += best_delta
            changed = True

    return used

def trim(route, used):
    value = route_value(route)

    while used > limit and len(route) > 2 and time.perf_counter() < deadline:
        cut = -1
        best_saved = 1
        best_lost = 0

        for i in range(1, len(route) - 1):
            a0 = route[i - 1]
            x = route[i]
            b0 = route[i + 1]

            bridge = 0 if a0 == b0 else mat[a0][b0]
            if a0 != b0 and bridge == 0:
                continue

            saved = mat[a0][x] + serv[x] + mat[x][b0] - bridge

            if saved <= 0:
                saved = 1

            lost = prize[x]

            if cut < 0 or lost * best_saved < best_lost * saved or (
                lost * best_saved == best_lost * saved and lost < best_lost
            ):
                cut = i
                best_saved = saved
                best_lost = lost

        if cut < 0:
            break

        a0 = route[cut - 1]
        x = route[cut]
        b0 = route[cut + 1]
        bridge = 0 if a0 == b0 else mat[a0][b0]

        used -= mat[a0][x] + serv[x] + mat[x][b0] - bridge
        value -= prize[x]
        del route[cut]

    if used <= limit:
        save_best(route, value, used)

    return used, value

def improve(route):
    used = route_time(route)

    if used >= inf:
        return

    used = shorten(route, used)

    if used > limit:
        used, value = trim(route, used)
    else:
        value = route_value(route)
        save_best(route, value, used)

    if used <= limit:
        for mode in (1, 2, 3, 4):
            if time.perf_counter() >= deadline:
                break

            trial = route[:]
            t_used = used
            val = value

            t_used, val = fill(trial, t_used, val, mode)
            t_used = shorten(trial, t_used)
            save_best(trial, route_value(trial), t_used)

def insertion_seed(mode):
    route = [0, 0]
    used = 0
    value = 0

    used, value = fill(route, used, value, mode)
    improve(route)

def forward_seed(mode, first=0):
    used_flag = bytearray(n)
    used_flag[0] = 1

    route = [0]
    cur = 0
    used = 0
    value = 0

    if first:
        go = mat[0][first]
        back = mat[first][0]

        if go == 0 or back == 0 or go + serv[first] + back > limit:
            return

        route.append(first)
        used_flag[first] = 1
        cur = first
        used = go + serv[first]
        value = prize[first]

    while time.perf_counter() < deadline:
        back = mat[cur][0]

        if cur and back and used + back <= limit:
            save_best(route + [0], value, used + back)

        choose = -1
        cost = 0
        best_key = None
        row = mat[cur]

        for v in nodes:
            if used_flag[v]:
                continue

            go = row[v]
            back = mat[v][0]

            if go == 0 or back == 0:
                continue

            add = go + serv[v]

            if used + add + back > limit:
                continue

            pv = prize[v]

            if mode == 0:
                key = (add, -pv, v)
            elif mode == 1:
                key = (-(pv * 10000019 // max(1, add)), add, v)
            elif mode == 2:
                key = (-pv, add, v)
            else:
                key = (-(pv * 10000019 // max(1, add + back)), add + back, v)

            if best_key is None or key < best_key:
                best_key = key
                choose = v
                cost = add

        if choose < 0:
            break

        route.append(choose)
        used_flag[choose] = 1
        used += cost
        value += prize[choose]
        cur = choose

    if cur and mat[cur][0] and used + mat[cur][0] <= limit:
        route.append(0)
        improve(route)

def nearest_seed():
    used_flag = bytearray(n)
    used_flag[0] = 1

    route = [0]
    cur = 0

    for _ in range(n - 1):
        row = mat[cur]
        choose = -1
        dist = 0

        for v in nodes:
            if used_flag[v]:
                continue

            w = row[v]

            if w == 0:
                continue

            if choose < 0 or w < dist or (w == dist and v < choose):
                choose = v
                dist = w

        if choose < 0:
            break

        route.append(choose)
        used_flag[choose] = 1
        cur = choose

    while len(route) > 1 and mat[route[-1]][0] == 0:
        route.pop()

    if len(route) > 1:
        route.append(0)
        improve(route)

for mode in (0, 1, 2, 3, 4):
    if time.perf_counter() >= deadline:
        break
    insertion_seed(mode)

for mode in (0, 1, 2, 3):
    if time.perf_counter() >= deadline:
        break
    forward_seed(mode)

start_order = nodes[:]
start_order.sort(
    key=lambda v: (
        -(prize[v] * 10000019 // max(1, serv[v] + (mat[0][v] or 10 ** 18) + (mat[v][0] or 10 ** 18))),
        -prize[v],
        v,
    )
)

first_limit = 50 if n > 55 else n - 1

for v in start_order[:first_limit]:
    if time.perf_counter() >= deadline:
        break
    forward_seed(1, v)

nearest_seed()

if best_value <= 0:
    sys.stdout.write("0\n0 0\n")
else:
    sys.stdout.write(str(best_value))
    sys.stdout.write("\n")
    sys.stdout.write(" ".join(map(str, best_route)))
    sys.stdout.write("\n")

if name == "main":
main()
