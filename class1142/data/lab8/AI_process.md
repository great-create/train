# AI 協作過程

## 1. 問題理解

我先根據 Lab8 投影片整理需求：

- 需要設計一個工廠機台排程系統。
- Producer 會生產物品並放入 buffer。
- 每個物品包含生產日期時間與 100 到 999 的 ID。
- Consumer / Machine 需要優先處理 buffer 中 ID 最小的物品。
- 題目提示使用 Heap，並要求把 C 寫的 Buffer 改成 Min Heap。

## 2. 與 AI 討論的重點

我詢問 AI：

1. 如何用 Min Heap 快速找出最小 ID？
2. Java GUI 如何啟動 Producer thread 與 Consumer thread？
3. Java 如何與 C 撰寫的 Buffer 配合？
4. 如何避免 buffer 滿時 Producer 繼續塞資料？
5. 如何讓 GUI 顯示目前 buffer 內容與執行紀錄？

## 3. AI 給出的設計方向

AI 建議：

- C 程式負責保存 buffer，並使用 Min Heap 管理資料。
- Java 使用 `ProcessBuilder` 啟動 C 程式，透過標準輸入輸出傳送指令。
- Java Producer thread 每 0.2 秒產生一筆資料。
- Java Consumer thread 每 0.24 秒取出 Min Heap 根節點，也就是目前 ID 最小的物品。
- Java GUI 使用 Swing 顯示 buffer 狀態與處理紀錄。

## 4. 程式改善過程

原本可用 Java 的 List 搭配 `stream().min()` 找最小值，但每次尋找都要掃過整個 buffer，時間複雜度為 O(n)。

後來改成 C 語言 Min Heap：

- 新增物品：O(log n)
- 取出最小 ID：O(log n)
- 查看最小值位置：heap root，也就是陣列索引 1

因此比每次線性搜尋更適合用在 buffer 變大時的排程問題。
