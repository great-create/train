import sys
import time

try:
sys.set_int_max_str_digits(0)
except Exception:
pass

def main():
try:
data = sys.stdin.buffer.read()
parts = data.split()
if not parts:
sys.stdout.write("0\n0 0\n")
return

    try:
        ptr = 0
        n = int(parts[ptr]); ptr += 1
        limit = int(parts[ptr]); ptr += 1
        prize = [0] * n
        service = [0] * n
        for i in range(n):
            prize[i] = int(parts[ptr]); ptr += 1
            service[i] = int(parts[ptr]); ptr += 1
        cost = []
        for _ in range(n):
            row = [0] * n
            for j in range(n):
                row[j] = int(parts[ptr]); ptr += 1
            cost.append(row)
    except Exception:
        import re
        nums = re.findall(rb"-?\d+", data)
        if len(nums) < 2:
            sys.stdout.write("0\n0 0\n")
            return
        ptr = 0
        n = int(nums[ptr]); ptr += 1
        limit = int(nums[ptr]); ptr += 1
        if n <= 0 or len(nums) < 2 + 2 * n + n * n:
            sys.stdout.write("0\n0 0\n")
            return
        prize = [0] * n
        service = [0] * n
        for i in range(n):
            prize[i] = int(nums[ptr]); ptr += 1
            service[i] = int(nums[ptr]); ptr += 1
        cost = []
        for _ in range(n):
            row = [0] * n
            for j in range(n):
                row[j] = int(nums[ptr]); ptr += 1
            cost.append(row)

    if n <= 1:
        sys.stdout.write("0\n0 0\n")
        return

    end_time = time.time() + 6.55
    big = 10 ** 80
    nodes = list(range(1, n))
    ret0 = [cost[i][0] for i in range(n)]

    min_in = [big] * n
    min_out = [big] * n

    for i in range(n):
        row = cost[i]
        mo = big
        for j in range(n):
            w = row[j]
            if i != j and w:
                if w < mo:
                    mo = w
                if w < min_in[j]:
                    min_in[j] = w
        min_out[i] = mo

    ans_score = 0
    ans_time = 0
    ans_path = [0, 0]

    def measure(route):
        if route == [0, 0]:
            return 0, 0, True
        if len(route) < 2 or route[0] != 0 or route[-1] != 0:
            return 0, big, False

        seen = bytearray(n)
        val = 0
        used = 0
        prev = 0

        for idx in range(1, len(route)):
            v = route[idx]

            if v < 0 or v >= n or v == prev:
                return 0, big, False

            w = cost[prev][v]
            if w == 0:
                return 0, big, False

            used += w

            if v:
                if seen[v]:
                    return 0, big, False
                seen[v] = 1
                used += service[v]
                val += prize[v]

            prev = v

        return val, used, used <= limit

    def keep(route, val=None, used=None):
        nonlocal ans_score, ans_time, ans_path

        if val is None or used is None:
            val2, used2, ok = measure(route)
            if not ok:
                return
            val = val2
            used = used2
        elif used > limit:
            return

        if val > ans_score or (val == ans_score and val > 0 and (ans_time == 0 or used < ans_time)):
            ans_score = val
            ans_time = used
            ans_path = route[:]

    def add_delta(route, pos, v):
        a = route[pos]
        b = route[pos + 1]

        av = cost[a][v]
        vb = cost[v][b]

        if av == 0 or vb == 0:
            return None

        if a == 0 and b == 0 and len(route) == 2:
            old = 0
        else:
            old = cost[a][b]
            if old == 0:
                return None

        return av + service[v] + vb - old

    def greedy_insert(route, used, val, rule):
        inside = bytearray(n)
        for x in route:
            inside[x] = 1

        while time.time() < end_time:
            best_v = -1
            best_pos = -1
            best_add = 0
            best_key = None
            length = len(route)

            for v in nodes:
                if inside[v]:
                    continue

                pv = prize[v]

                for pos in range(length - 1):
                    extra = add_delta(route, pos, v)

                    if extra is None or used + extra > limit:
                        continue

                    e = extra if extra > 0 else 1

                    if rule == 0:
                        key = (extra, -pv, v, pos)
                    elif rule == 1:
                        key = (-(pv * 1000003 // e), extra, v, pos)
                    elif rule == 2:
                        key = (-pv, extra, v, pos)
                    elif rule == 3:
                        key = (-(pv - extra), extra, v, pos)
                    else:
                        mi = min_in[v] if min_in[v] < big else 0
                        mo = min_out[v] if min_out[v] < big else 0
                        den = service[v] + mi + mo
                        if den <= 0:
                            den = e
                        key = (-(pv * 1000003 // den), extra, v, pos)

                    if best_key is None or key < best_key:
                        best_key = key
                        best_v = v
                        best_pos = pos + 1
                        best_add = extra

            if best_v < 0:
                break

            route.insert(best_pos, best_v)
            inside[best_v] = 1
            used += best_add
            val += prize[best_v]
            keep(route, val, used)

        return used, val

    def shorten(route, used):
        changed = True
        loops = 0

        while changed and loops < 5 and time.time() < end_time:
            loops += 1
            changed = False
            best = 0
            move = None
            m = len(route)

            for i in range(1, m - 1):
                x = route[i]
                a = route[i - 1]
                b = route[i + 1]
                bridge = cost[a][b]

                if bridge == 0:
                    continue

                remove_change = bridge - cost[a][x] - service[x] - cost[x][b]

                for pos in range(m - 1):
                    if pos == i - 1 or pos == i:
                        continue

                    c = route[pos]
                    d = route[pos + 1]
                    old = cost[c][d]

                    if old == 0:
                        continue

                    cx = cost[c][x]
                    xd = cost[x][d]

                    if cx == 0 or xd == 0:
                        continue

                    delta = remove_change + cx + service[x] + xd - old

                    if delta < best:
                        best = delta
                        move = (0, i, pos)

                if time.time() >= end_time:
                    break

            if move is not None:
                _, i, pos = move
                x = route.pop(i)
                if pos > i:
                    pos -= 1
                route.insert(pos + 1, x)
                used += best
                changed = True
                continue

            m = len(route)
            window = 42 if m > 70 else m

            for i in range(1, m - 2):
                a = route[i - 1]
                left = route[i]
                old_a = cost[a][left]

                if old_a == 0:
                    continue

                stop = i + window
                if stop > m - 1:
                    stop = m - 1

                for j in range(i + 1, stop):
                    right = route[j]
                    b = route[j + 1]

                    ar = cost[a][right]
                    lb = cost[left][b]

                    if ar == 0 or lb == 0:
                        continue

                    old_mid = 0
                    new_mid = 0
                    ok = True

                    for k in range(i, j):
                        old_mid += cost[route[k]][route[k + 1]]
                        rw = cost[route[k + 1]][route[k]]

                        if rw == 0:
                            ok = False
                            break

                        new_mid += rw

                    if not ok:
                        continue

                    delta = ar + new_mid + lb - old_a - old_mid - cost[right][b]

                    if delta < best:
                        best = delta
                        move = (1, i, j)

                if time.time() >= end_time:
                    break

            if move is not None:
                _, i, j = move
                route[i:j + 1] = route[i:j + 1][::-1]
                used += best
                changed = True

        return used

    def remove_until_fit(route, used):
        val = 0
        for x in route:
            if x:
                val += prize[x]

        while used > limit and len(route) > 2 and time.time() < end_time:
            cut = -1
            cmp_loss = 0
            cmp_save = 1

            for i in range(1, len(route) - 1):
                a = route[i - 1]
                x = route[i]
                b = route[i + 1]
                bridge = cost[a][b]

                if bridge == 0:
                    continue

                saved = cost[a][x] + service[x] + cost[x][b] - bridge

                if saved <= 0:
                    saved = 1

                loss = prize[x]

                if cut < 0 or loss * cmp_save < cmp_loss * saved:
                    cut = i
                    cmp_loss = loss
                    cmp_save = saved

            if cut < 0:
                break

            a = route[cut - 1]
            x = route[cut]
            b = route[cut + 1]
            bridge = cost[a][b]

            used -= cost[a][x] + service[x] + cost[x][b] - bridge
            val -= prize[x]
            del route[cut]

        if used <= limit:
            keep(route, val, used)

        return used, val

    def finish(route):
        val, used, _ = measure(route)

        if used >= big:
            return

        used = shorten(route, used)

        if used > limit:
            used, val = remove_until_fit(route, used)
        else:
            val = 0
            for x in route:
                if x:
                    val += prize[x]
            keep(route, val, used)

        if used <= limit:
            for rule in (1, 2, 0, 3, 4):
                if time.time() >= end_time:
                    break

                trial = route[:]
                tv = val
                tu = used

                tu, tv = greedy_insert(trial, tu, tv, rule)
                tu = shorten(trial, tu)

                vv, uu, ok = measure(trial)
                if ok:
                    keep(trial, vv, uu)

    def seed_by_insertion(rule):
        r = [0, 0]
        u, v = greedy_insert(r, 0, 0, rule)
        keep(r, v, u)
        finish(r)

    def seed_by_walk(rule, first=0):
        seen = bytearray(n)
        seen[0] = 1

        r = [0]
        cur = 0
        used = 0
        val = 0

        if first:
            go = cost[0][first]
            bk = ret0[first]

            if go == 0 or bk == 0 or go + service[first] + bk > limit:
                return

            r.append(first)
            seen[first] = 1
            cur = first
            used = go + service[first]
            val = prize[first]

        while time.time() < end_time:
            bk = ret0[cur]

            if cur and bk and used + bk <= limit:
                keep(r + [0], val, used + bk)

            chosen = -1
            add = 0
            best_key = None
            row = cost[cur]
            remain = limit - used

            for v in nodes:
                if seen[v]:
                    continue

                go = row[v]
                bk = ret0[v]

                if go == 0 or bk == 0:
                    continue

                extra = go + service[v]

                if extra + bk > remain:
                    continue

                pv = prize[v]
                e = extra if extra > 0 else 1

                if rule == 0:
                    key = (extra, -pv, v)
                elif rule == 1:
                    key = (-(pv * 1000003 // e), extra, v)
                elif rule == 2:
                    key = (-pv, extra, v)
                else:
                    key = (-(pv * 1000003 // max(1, extra + bk)), extra + bk, v)

                if best_key is None or key < best_key:
                    best_key = key
                    chosen = v
                    add = extra

            if chosen < 0:
                break

            r.append(chosen)
            seen[chosen] = 1
            used += add
            val += prize[chosen]
            cur = chosen

        bk = ret0[cur]

        if cur and bk and used + bk <= limit:
            r.append(0)
            finish(r)

    def seed_nearest_all():
        seen = bytearray(n)
        seen[0] = 1

        r = [0]
        cur = 0

        for _ in range(n - 1):
            row = cost[cur]
            pick = -1
            dist = 0

            for v in nodes:
                if seen[v]:
                    continue

                w = row[v]

                if w == 0:
                    continue

                if pick < 0 or w < dist or (w == dist and prize[v] > prize[pick]):
                    pick = v
                    dist = w

            if pick < 0:
                break

            r.append(pick)
            seen[pick] = 1
            cur = pick

        while len(r) > 1 and ret0[r[-1]] == 0:
            r.pop()

        if len(r) == 1:
            return

        r.append(0)

        present = bytearray(n)
        for x in r:
            present[x] = 1

        changed = True

        while changed and time.time() < end_time:
            changed = False

            for v in nodes:
                if present[v]:
                    continue

                best_pos = -1
                best_extra = None

                for pos in range(len(r) - 1):
                    d = add_delta(r, pos, v)

                    if d is None:
                        continue

                    if best_extra is None or d < best_extra:
                        best_extra = d
                        best_pos = pos + 1

                if best_pos >= 0:
                    r.insert(best_pos, v)
                    present[v] = 1
                    changed = True

        finish(r)

    for mode in (0, 1, 2, 3, 4):
        if time.time() >= end_time:
            break
        seed_by_insertion(mode)

    for mode in (0, 1, 2, 3):
        if time.time() >= end_time:
            break
        seed_by_walk(mode)

    start_list = nodes[:]
    start_list.sort(
        key=lambda x: (
            -(prize[x] * 1000003 // max(1, service[x] + (cost[0][x] or 10 ** 30) + (ret0[x] or 10 ** 30))),
            -prize[x],
            x,
        )
    )

    lim = 45 if n > 50 else n - 1

    for x in start_list[:lim]:
        if time.time() >= end_time:
            break
        seed_by_walk(1, x)

    seed_nearest_all()

    if ans_score <= 0:
        sys.stdout.write("0\n0 0\n")
    else:
        sys.stdout.write(str(ans_score))
        sys.stdout.write("\n")
        sys.stdout.write(" ".join(map(str, ans_path)))
        sys.stdout.write("\n")

except Exception:
    sys.stdout.write("0\n0 0\n")

if name == "main":
main()
