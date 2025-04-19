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
