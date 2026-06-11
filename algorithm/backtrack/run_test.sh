#!/usr/bin/env bash
# 用法: ./run_test.sh <程式.py> <測資.in> [時間限制秒數=8] [最佳解out=可選]
# 會顯示耗時、是否 TLE，並（若給 .out）比對是否達最佳解
PROG="$1"; IN="$2"; LIMIT="${3:-8}"; EXP="$4"
if [ -z "$PROG" ] || [ -z "$IN" ]; then
  echo "用法: ./run_test.sh <程式.py> <測資.in> [限制秒數] [最佳解.out]"; exit 2
fi
echo "執行 $PROG  測資 $IN  限制 ${LIMIT}s"
start=$(date +%s.%N)
OUT_TXT=$(timeout "${LIMIT}s" python3 "$PROG" < "$IN")
rc=$?
end=$(date +%s.%N)
el=$(awk "BEGIN{printf \"%.2f\", $end-$start}")
if [ $rc -eq 124 ]; then
  echo "→ 結果：TLE 超時（> ${LIMIT}s）❌"
  exit 1
elif [ $rc -ne 0 ]; then
  echo "→ 結果：程式錯誤（exit=$rc）"
  exit 1
fi
echo "→ 完成，耗時 ${el}s ✅"
got=$(printf '%s\n' "$OUT_TXT" | head -1)
echo "→ 宣告獎勵：$got"
if [ -n "$EXP" ] && [ -f "$EXP" ]; then
  exp=$(head -1 "$EXP")
  if [ "$got" == "$exp" ]; then echo "→ 與最佳解 $exp 相同 ✓（達最佳解）"
  else echo "→ 最佳解為 $exp（此程式合法但非最佳）"; fi
fi
