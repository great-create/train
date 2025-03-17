/*倒印字串
Description

請撰寫一個遞迴函式stringReverse，請依題目指示命名，若無則不予計分。
它的引數為一個字元陣列，將此陣列倒過來列印，沒有回傳值。
這個函式應在遇到字串的【結束空字元】時，停止處理並返回。
程式可重複輸入，直到字串判斷為空，則停止該程式。

(Print a String Backward) Write a recursive functionstringReversethat takes a character array as an argument, prints it back to front and returns nothing.
The function should stop processing and return when the terminating null character of the string is encountered.


Input

輸入一個字串

Input a string.


Output

印出反轉後的字。

Output the reversed string.


Sample Input 1 

Hello
abc def
Sample Output 1

olleH
fed cba
Language: 
*/#include <stdio.h>
#include <string.h>
#define SIZE 20
void stringReverse(char c[]);

int main() {
    
    char num[SIZE];  
    
/*此程式會變成逐字串，找空字元。但考試時，是輸入兩三段以上字串，看程式是否正確while(1){
    fgets(num, sizeof(num), stdin);
        
    
    // 移除換行符號
    num[strcspn(num, "\n")] = '\0';
        
    if (num[0] == '\0') {
        break;
        }

        
    stringReverse(num); 
    printf("\n");
    }*/    
    while(fgets(num, sizeof(num), stdin)){
    
        
    
        // 移除換行符號
        num[strcspn(num, "\n")] = '\0';
        
        
        
        stringReverse(num); 
     	printf("\n");
    }
    return 0;
}

void stringReverse(char c[]){
    if (*c == '\0') {
        return;
    }
    stringReverse(c + 1);
    printf("%c", *c);
    
}
