#!/usr/bin/env bash
# 用法: bash run_dp_test.sh <程式.py> [時間限制秒數=8]
# 功能: 用 D_dp.in 餵程式，顯示耗時、是否超時(TLE)，並驗證輸出是否為合法最佳解。
PROG="$1"; LIMIT="${2:-8}"
IN="D_dp.in"; ANS="D_dp.out"
[ -z "$PROG" ] && { echo "用法: bash run_dp_test.sh <程式.py> [時間限制=8]"; exit 1; }
echo "測資: $IN   時間限制: ${LIMIT}s"
START=$(date +%s.%N)
OUT=$(timeout "${LIMIT}" python3 "$PROG" < "$IN"); EC=$?
END=$(date +%s.%N)
ELAPSED=$(echo "$END - $START" | bc)
if [ "$EC" -eq 124 ]; then
  printf "結果: ✗ 超時 TLE  (耗時 > %ss，被強制中止)\n" "$LIMIT"
  exit 2
fi
printf "耗時: %.3fs  (限制 %ss)\n" "$ELAPSED" "$LIMIT"
# 驗證合法性與最佳解
echo "$OUT" | python3 verify.py "$IN" "$ANS"
