import sys

def main():
data = sys.stdin.buffer.read().split()
if not data:
return

it = iter(data)
n = int(next(it))
t_max = int(next(it))

profit = [0] * n
service = [0] * n

for i in range(n):
    profit[i] = int(next(it))
    service[i] = int(next(it))

travel = [[0] * n for _ in range(n)]
for i in range(n):
    row = travel[i]
    for j in range(n):
        row[j] = int(next(it))

visited = [False] * n
visited[0] = True

path = [0]
total_time = 0
total_profit = 0
current = 0

while True:
    best = -1
    best_cost = 10**30

    row = travel[current]
    for i in range(1, n):
        if visited[i]:
            continue

        go = row[i]
        back = travel[i][0]

        if go == 0 or back == 0:
            continue

        cost = go + service[i]
        if total_time + cost + back > t_max:
            continue

        if cost < best_cost:
            best_cost = cost
            best = i

    if best == -1:
        break

    total_time += best_cost
    total_profit += profit[best]
    visited[best] = True
    path.append(best)
    current = best

if len(path) == 1:
    sys.stdout.write("0\n0 0")
else:
    path.append(0)
    sys.stdout.write(str(total_profit) + "\n" + " ".join(map(str, path)))

if name == "main":
main()
