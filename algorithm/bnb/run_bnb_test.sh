#!/usr/bin/env bash
# 用法: bash run_bnb_test.sh <程式.py> [時間限制秒數=8]
# 用 D_bnb.in 餵程式，顯示耗時、是否超時(TLE)/崩潰，並驗證是否為合法最佳解。
# 僅需 python3 與 timeout。
PROG="$1"; LIMIT="${2:-8}"
IN="D_bnb.in"; ANS="D_bnb.out"
[ -z "$PROG" ] && { echo "用法: bash run_bnb_test.sh <程式.py> [時間限制=8]"; exit 1; }
[ -f "$IN" ]  || { echo "找不到 $IN（請在測資所在資料夾執行）"; exit 1; }
[ -f "$PROG" ] || { echo "找不到程式: $PROG"; exit 1; }
echo "測資: $IN   時間限制: ${LIMIT}s"
START=$(date +%s.%N)
OUT=$(timeout "${LIMIT}" python3 "$PROG" < "$IN"); EC=$?
END=$(date +%s.%N)
ELAPSED=$(python3 -c "print('%.3f' % ($END - $START))" 2>/dev/null || echo "?")
if [ "$EC" -eq 124 ]; then echo "結果: ✗ 超時 TLE  (耗時 > ${LIMIT}s，被強制中止)"; exit 2; fi
if [ "$EC" -ne 0 ]; then echo "結果: ✗ 異常結束 (exit=$EC，常見為記憶體不足或執行期錯誤)；耗時約 ${ELAPSED}s"; exit 3; fi
echo "耗時: ${ELAPSED}s  (限制 ${LIMIT}s)"
printf '%s\n' "$OUT" | python3 verify.py "$IN" "$ANS"
