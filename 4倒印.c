最近在Nlogonia的地震並未對首都的建築物造成太大影響，而該地正是地震的震央。

但科學家們發現地震對堤壩牆造成了影響，目前其地下部分存在著重大結構損壞，若不迅速修復，可能導致堤壩倒塌，進而淹沒整個首都。

修復工作必須由潛水員在極為困難和危險的條件下，在深淵中進行。

但由於城市的生存受到威脅，居民們紛紛自願參與這項危險任務。

如同危險任務中的傳統一樣，每位潛水員在開始任務時都收到一張帶有識別號碼的小卡片。

在完成任務後，志願者將名牌歸還，放入存儲庫中。

堤壩已經再次安全，但不幸的是，似乎有些志願者沒有從他們的任務中返回。

你被聘用來從存儲庫中放置的名牌中確定哪些志願者為拯救城市而犧牲了自己的生命。

-------------------------------------------------------------------------------

The recent earthquake in Nlogonia did not affect too much the buildings in the capital, which was at the epicenter of the quake.

But the scientists found that it affected the dike wall, which now has a significant structural failure in its underground part that, if not repaired quickly, can cause the collapse of the dike, with the consequent flooding the whole capital.

The repair must be done by divers, at a large depth, under extremely difficult and dangerous conditions.

But since the survival of the city is at stake, its residents came out in large numbers to volunteer for this dangerous mission.

As is traditional in dangerous missions, each diver received at the start of his/her mission a small card with an identification number.

At the end of their mission, the volunteers returned the nameplate, placing it in a repository.

The dike is safe again, but unfortunately it seems that some volunteers did not return from their missions.

You were hired for the grueling task of, given the plates placed in the repository, determine which volunteers lost their lives to save the city.


Input

輸入包含多個測試案例。每個測試案例由兩行組成。

第一行包含兩個整數 N 和 R，分別表示參與任務的志願者數量和返回任務的志願者數量。

志願者通過從 1 到 N 的數字進行識別。

第二行包含 R 個整數，表示返回任務的志願者（至少有一名志願者返回）。

-------------------------------------------------------------------------------

The input contains several test cases. Each test case is composed of two lines.

The first line contains two integers N and R, indicating respectively the number of volunteers that went to the mission and the number of volunteers that returned from the mission.

Volunteers are identified by numbers from 1to N.

The second line contains R integers, indicating the volunteers which returned from the mission(at least one volunteer returned).


Output

對於每個測試案例，您的程式必須產生一行，其中包含未從任務中返回的志願者的識別符，按其識別符升序排列。

在每個識別符後面留一個空格（請注意，因此在行末必須在最後一個識別符後面留一個空格）。

如果每個志願者都返回了，該行必須包含一個單獨的字符 '*'（星號）。

限制

1 ≤ R ≤N ≤ 10^4
-------------------------------------------------------------------------------

For each test case your program must produce a single line containing the identifiers of the volunteers who did not return from their missions, in ascending order of their identifications.

Leave a blank space after each identifier (notice that, therefore, there must be a blank space after the last identifier in the line).

If every volunteer returned, the line must contain a single character ‘*’ (asterisk).


Sample Input 1 

5 3
3 1 5
6 6
6 1 3 2 5 4
Sample Output 1

2 4
*

START 1000
I     BYTE 1               ; 初始 i=1
J     BYTE 1               ; 初始 j=1
RESULT WORD ?              ; 儲存乘積結果
TEXTBUF RESB 40            ; 暫存輸出文字

      LDA I                ; A = I
      COMP =X'09'          ; 比較是否到9
      JGT ENDPROG          ; 若 >9，跳到結束

LOOPI LDA I                ; A = I
      STA TEMP_I           ; 儲存 I 到暫存變數
      LDB =1               ; B = j = 1

LOOPJ LDA TEMP_I           ; A = I
      MUL B                ; A = I * J
      STA RESULT           ; 存入 RESULT

* 若要輸出，可在模擬器中定義輸出例程，如 DUMP RESULT
* 模擬器可顯示 RESULT 的值

      ADD B, =1            ; j++
      COMP B, =9
      JGT NEXTI
      J     LOOPJ

NEXTI LDA I
      ADD A, =1            ; i++
      STA I
      J     LOOPI

ENDPROG
      RSUB

TEMP_I  WORD ?
      END START
