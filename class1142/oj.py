import subprocess

try:
    result = subprocess.run(
        ["python", "other_code.py"],
        input=open("adversarial_bigint_matrix.in", "rb").read(),
        stdout=subprocess.PIPE,
        timeout=120
    )

    expected = open("adversarial_bigint_matrix.out", "rb").read()

    if result.stdout == expected:
        print("✅ AC（正確且未超時）")
    else:
        print("❌ WA（結果錯誤）")

except subprocess.TimeoutExpired:
    print("⛔ TLE（超時）")
