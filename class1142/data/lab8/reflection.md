# 自行改進說明與反思

## 自行改進說明

本次實作除了完成 Producer 與 Consumer thread，也將 buffer 的資料結構改成 Min Heap。

我做的改進如下：

1. 使用 Min Heap 取代線性搜尋
   - 原本若用 `buffer.stream().min()`，每次取最小 ID 都需要 O(n)。
   - 改用 Min Heap 後，取出最小 ID 的時間為 O(log n)。

2. Producer 與 Consumer 分開執行
   - Producer thread 負責生產物品。
   - Consumer thread 負責從 buffer 取出最小 ID 的物品。
   - 兩者可以同時運作，符合投影片要求的 Thread 概念。

3. GUI 同時顯示 Buffer 與 Log
   - 左側顯示目前 buffer 內容。
   - 右側顯示 Produced 與 Consumed 的紀錄。
   - 使用者可以直接觀察系統是否正常運作。

4. Java 與 C 分工
   - Java 負責 GUI 與執行緒控制。
   - C 負責 Min Heap Buffer。
   - 這樣可以符合「Buffer 用 C 撰寫，Java 程式可以呼叫 C 所寫的 Buffer 資料」的要求。

## 反思

這次練習讓我理解 Heap 適合用在「反覆取出最小值或最大值」的情境。

若 buffer 內資料很少，線性搜尋與 Heap 的差異不一定明顯；但當 buffer 變大，或 Producer 與 Consumer 長時間運作時，Heap 的效率會更穩定。

此外，Thread 雖然可以讓 Producer 與 Consumer 同時執行，但也要注意共享資源的同步問題。本次 Java 呼叫 C buffer 時，我使用同步鎖保護指令傳送，避免 Producer 與 Consumer 同時對 C 程式送指令造成資料錯亂。

未來如果要再改進，可以加入：

- 暫停與繼續按鈕
- 顯示目前處理速度
- 顯示已生產與已消費總數
- 使用 JNI 或 JNA 讓 Java 更直接呼叫 C 函式
