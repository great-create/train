import sys


def main():
    # 一次讀完所有輸入；bytes token 只在需要時各轉一次 int（支援超大整數）
    data = sys.stdin.buffer.read().split()
    pos = 0
    N = int(data[pos]); pos += 1
    T_max = int(data[pos]); pos += 1

    # 獎勵 p[i] 與服務時間 s[i]：每個 token 只轉換一次
    p = [0] * N
    s = [0] * N
    for i in range(N):
        p[i] = int(data[pos]); pos += 1
        s[i] = int(data[pos]); pos += 1

    # 行駛時間矩陣，以「列為單位」存成 list of list：
    # 每筆只轉一次 int，且不另外建立轉置或暫存矩陣
    rows = [None] * N
    for i in range(N):
        base = pos + i * N
        rows[i] = [int(x) for x in data[base:base + N]]
    pos += N * N

    del data  # 提早釋放原始 token list，降低超大輸入時的記憶體峰值

    # 回倉時間 back[j] = t[j][0]（只取第 0 欄，非整個矩陣的副本）
    back = [rows[i][0] for i in range(N)]

    visited = bytearray(N)   # bytearray 比 list of bool 更省記憶體、存取更快
    visited[0] = 1
    cur = 0
    time_used = 0
    total = 0
    route = [0]

    while True:
        row = rows[cur]              # 先把當前列取出一次，減少重複索引成本
        rem = T_max - time_used
        best_j = -1
        best_p = 0                   # 以 best_p / best_cost 代表目前最佳 CP 值
        best_cost = 1
        for j in range(1, N):
            if visited[j]:
                continue
            tij = row[j]
            if tij == 0:             # j != cur，故 0 代表此路不通
                continue
            bj = back[j]
            if bj == 0:              # 無法由 j 直接回倉 -> 略過，確保路徑必定可合法收尾
                continue
            cost = tij + s[j]        # 抵達並服務 j 所需的新增時間
            if cost + bj > rem:      # 可行性：含直接回倉是否仍在 T_max 內
                continue
            pj = p[j]
            # 選「單位時間獎勵」最大者；以整數交叉相乘比較，避免 float 對超大整數溢位/失準
            #   pj/cost > best_p/best_cost  <=>  pj*best_cost > best_p*cost
            if best_j == -1 or pj * best_cost > best_p * cost:
                best_j = j; best_p = pj; best_cost = cost

        if best_j == -1:
            break
        time_used += row[best_j] + s[best_j]
        total += p[best_j]
        visited[best_j] = 1
        route.append(best_j)
        cur = best_j

    route.append(0)

    # 不使用 print：直接寫入 stdout buffer
    out = sys.stdout
    out.write(str(total))
    out.write("\n")
    out.write(" ".join(map(str, route)))
    out.write("\n")


main()
