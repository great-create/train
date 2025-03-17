/*陣列(指標)
Description

請使用指標撰寫一個輸出函式（output），用於輸出一個整數陣列，直到輸入0結束程式。

Using aPointerto write a output function to output an integer array using pointers till input 0.


Input

輸入5個整數，將5個整數存入一個陣列A。

Input 5 integers and store the 5 integers inan A array.


Output

輸出已存放5個整數的數列。

Output an array of 5 integers.


Sample Input 1 

5
1 2 3 4 5
10
9 8 7 6 5 4 3 2 1 0
7
123 456 789 555 666 888 9999
0
Sample Output 1

A[5]={1,2,3,4,5}
A[10]={9,8,7,6,5,4,3,2,1,0}
A[7]={123,456,789,555,666,888,9999}
Hint

函式需命名為output並使用指標，若為非則不計分。

*/
#include <stdio.h>

void output(int *arr, int size) {
    // 輸出陣列
    printf("A[%d]={", size);
    for (int i = 0; i < size; i++) {
        printf("%d", *(arr + i));  // 使用指標存取陣列元素
        if (i != size - 1) {
            printf(",");  // 如果不是最後一個元素，加上逗號
        }
    }
    printf("}\n");
}

int main() {
    int A[100];  // 陣列大小設為100，以應對可能的多次輸入
    int n;
    
    while (1) {
        scanf("%d", &n);
        if (n == 0) {
            break;  // 當輸入為0時退出
        }
        
        // 讀取 n 個整數並存入陣列 A 中
        for (int i = 0; i < n; i++) {
            scanf("%d", &A[i]);
        }
        
        // 呼叫 output 函式來輸出陣列
        output(A, n);
    }
    
    return 0;
}

