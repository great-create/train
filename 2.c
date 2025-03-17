/*swap(指標)
Description

請使用指標撰寫一個交換函式(swap)，交換兩個整數值。

請依照題目要求命名，若無則不予計分。

Write a swap functionthat swaps two integer values usingpointers.


Input

輸入兩個整數，直到兩個整數都為0終止程式。

Input two integers until both integers are 0 to terminate the program.


Output

輸出交換位置後的兩個整數。

Output the two integers with their positions swapped.


Sample Input 1 

12 34
56 78
910 1112
0 0
Sample Output 1

34 12
78 56
1112 910*/

/* Online C Compiler and Editor */
#include <stdio.h>
void swap(int *,int *);


int main()
{
    int a,b;
    while(1){
        scanf("%d %d",&a,&b);
    
        if (a == 0 && b == 0) {
            break;
            }
        
        swap(&a, &b);
        printf("%d %d\n",a,b);
    }
    
    return 0;
}

void swap(int *a,int *b){
    int temp;
    
    temp = *a;
    *a = *b;
    *b = temp;
    
}