# Lab8 Heap 實作與應用

本作業依照投影片要求完成：

- Java GUI
- Producer thread：約每 0.2 秒產生一個物品
- Consumer thread：約每 0.24 秒取出 buffer 中 ID 最小的物品
- C 語言撰寫 Buffer
- C Buffer 使用 Min Heap，加速挑選最小 ID 物品
- GUI 顯示目前 Buffer 內容與 Producer/Consumer 執行紀錄

## 檔案說明

```text
src/MinHeapBuffer.c          C 語言 Min Heap Buffer
src/ProducerConsumerGUI.java Java Swing GUI 與 Producer/Consumer threads
docs/AI_process.md           AI 協作過程
docs/reflection.md           自行改進說明與反思
```

## Windows 編譯與執行

請在 `src` 資料夾內執行：

```bat
gcc MinHeapBuffer.c -o MinHeapBuffer.exe
javac ProducerConsumerGUI.java
java ProducerConsumerGUI
```

## Linux / macOS 編譯與執行

請在 `src` 資料夾內執行：

```bash
gcc MinHeapBuffer.c -o MinHeapBuffer
javac ProducerConsumerGUI.java
java ProducerConsumerGUI
```

## 執行截圖建議

執行 GUI 後：

1. 在 Buffer Size 輸入 10 或 15。
2. 按下 Start。
3. 等待畫面出現 Produced 與 Consumed lowest ID 紀錄。
4. 截圖 GUI 畫面，命名為 `screenshot_gui.png`。
5. 截圖編譯與執行指令畫面，命名為 `screenshot_run.png`。

最後把本資料夾壓縮成「學號.zip」上傳，避免使用中文檔名。
