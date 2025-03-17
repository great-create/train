/*將電話號碼切割成字符
Description

請撰寫一個程式將電話號碼以字串形式輸入，格式如(555)555-5555。

此程式應使用strtok函式(使用指標)將區碼萃取成一個字符、電話號碼的前三碼為一個字符，還有後四碼也萃取成一個字符。電話號碼的七個數字應串接成一個字串。

程式應把區碼字串轉換成int，把電話號碼字串轉換成long。最後印出區碼及電話號碼的值。

未使用strtok函式，將不予計分。


Input

依照題目要求格式輸入區碼開頭以及電話號碼開頭不為0的電話號碼，直到輸入為EOF，則停止程式。


Output

輸出區碼以及電話號碼，並使用" - "區隔。


Sample Input 1 

(555)555-5555
(600)222-3264
(123)100-1000
Sample Output 1

555 - 5555555
600 - 2223264
123 – 1001000*/

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main() {
    char num[20];  

    
    while (fgets(num, sizeof(num), stdin) != NULL) {
        
		num[strcspn(num, "\n")] = '\0';
        
        char *num_a = strtok(num, "()");
        char *num_b = strtok(NULL, "-");
        char *num_c = strtok(NULL,"");

       	if (num_a[0] == '0' || num_b[0] == '0') {
			continue; 
            }
        

        
        int num_int = atoi(num_a);
        
        
        char phone[20];
      	

        /*
        snprintf(phone,sizeof(phone),"%s%s",num_b,num_c);
      
        long phone_num = atoi(phone);

        */
        
        //不知為何錯誤: long phone_num = atoi(strcat(num_b,num_c));
        //不知為何會runtime=>long phone_num = atoi(snprintf(phone,sizeof(phone),"%s%s",num_b,num_c));
      	snprintf(phone,sizeof(phone),"%s%s",num_b,num_c);
      
        long phone_num = atoi(phone);
        

        
        printf("%d - %ld\n", num_int, phone_num);
    }

    return 0;

}