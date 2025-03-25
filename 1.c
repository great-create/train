#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_NAME_LENGTH 20

// 定義員工結構體
typedef struct {
    int id;             // 員工編號
    char name[MAX_NAME_LENGTH]; // 員工姓名
    double salary;      // 員工薪資
} Employee;

void addEmployeesToFile(FILE *file, int numEmployees) {
    Employee emp;
    for (int i = 0; i < numEmployees; i++) {
        // 輸入員工資料
        printf("Enter employee ID, name, and salary: ");
        scanf("%d %s %lf", &emp.id, emp.name, &emp.salary);
        // 將員工資料寫入二進位檔案
        fwrite(&emp, sizeof(Employee), 1, file);
    }
}

void queryEmployeeSalary(FILE *file, int queryId) {
    Employee emp;
    fseek(file, 0, SEEK_SET);  // 從檔案開頭開始讀取
    int found = 0;

    // 讀取所有員工資料並查找符合編號的員工
    while (fread(&emp, sizeof(Employee), 1, file)) {
        if (emp.id == queryId) {
            printf("%d %s %.2f\n", emp.id, emp.name, emp.salary);
            found = 1;
            break;
        }
    }

    if (!found) {
        printf("Employee not found\n");
    }
}

int main() {
    FILE *inputFile = fopen("input.dat", "rb");
    FILE *outputFile = fopen("output.dat", "wb");

    if (!inputFile || !outputFile) {
        printf("Error opening file!\n");
        return -1;
    }

    int numEmployees;
    fscanf(inputFile, "%d", &numEmployees);

    // 先將員工資料寫入二進位檔案
    addEmployeesToFile(inputFile, numEmployees);

    // 查詢員工薪資
    int queryId;
    fscanf(inputFile, "%d", &queryId);

    queryEmployeeSalary(inputFile, queryId);

    fclose(inputFile);
    fclose(outputFile);
    return 0;
}
