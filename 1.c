#include <stdio.h>

int main() {
    FILE *inputFile, *outputFile;
    char ch;
    
    // 開啟 input.txt 讀取模式
    inputFile = fopen("input.txt", "r");
    if (inputFile == NULL) {
        perror("無法開啟 input.txt");
        return 1;
    }
    
    // 開啟 output.txt 寫入模式
    outputFile = fopen("output.txt", "w");
    if (outputFile == NULL) {
        perror("無法開啟 output.txt");
        fclose(inputFile);
        return 1;
    }
    
    // 讀取 input.txt 的內容並寫入 output.txt
    while ((ch = fgetc(inputFile)) != EOF) {
        fputc(ch, outputFile);
    }
    
    // 加入換行符號
    fputc('\n', outputFile);
    
    // 重置 input.txt 的讀取位置
    rewind(inputFile);
    
    // 再次讀取 input.txt 並寫入 output.txt
    while ((ch = fgetc(inputFile)) != EOF) {
        fputc(ch, outputFile);
    }
    
    // 關閉檔案
    fclose(inputFile);
    fclose(outputFile);
    
    return 0;
}
