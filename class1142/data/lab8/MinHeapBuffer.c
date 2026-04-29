#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_CAPACITY 10000

typedef struct {
    int id;
    char time[64];
} Item;

static Item heap[MAX_CAPACITY + 1]; // 1-based index
static int size = 0;
static int capacity = 10;

static void swap(Item *a, Item *b) {
    Item t = *a;
    *a = *b;
    *b = t;
}

static int less_item(Item a, Item b) {
    if (a.id != b.id) return a.id < b.id;
    return strcmp(a.time, b.time) < 0;
}

static void heap_push(Item item) {
    int i;
    if (size >= capacity) {
        printf("FULL\n");
        fflush(stdout);
        return;
    }
    heap[++size] = item;
    i = size;
    while (i > 1 && less_item(heap[i], heap[i / 2])) {
        swap(&heap[i], &heap[i / 2]);
        i /= 2;
    }
    printf("OK\n");
    fflush(stdout);
}

static void heap_pop(void) {
    int parent, child;
    Item min_item;
    if (size == 0) {
        printf("EMPTY\n");
        fflush(stdout);
        return;
    }
    min_item = heap[1];
    heap[1] = heap[size--];

    parent = 1;
    while (parent * 2 <= size) {
        child = parent * 2;
        if (child + 1 <= size && less_item(heap[child + 1], heap[child])) child++;
        if (!less_item(heap[child], heap[parent])) break;
        swap(&heap[parent], &heap[child]);
        parent = child;
    }

    printf("ITEM %d %s\n", min_item.id, min_item.time);
    fflush(stdout);
}

static void print_snapshot(void) {
    int i;
    printf("SIZE %d\n", size);
    for (i = 1; i <= size; i++) {
        printf("%d %s\n", heap[i].id, heap[i].time);
    }
    printf("END\n");
    fflush(stdout);
}

int main(void) {
    char line[256];
    setvbuf(stdout, NULL, _IOLBF, 0);

    while (fgets(line, sizeof(line), stdin)) {
        if (strncmp(line, "INIT", 4) == 0) {
            int n;
            if (sscanf(line, "INIT %d", &n) == 1 && n > 0 && n <= MAX_CAPACITY) {
                capacity = n;
                size = 0;
                printf("OK\n");
            } else {
                printf("ERR invalid capacity\n");
            }
            fflush(stdout);
        } else if (strncmp(line, "ADD", 3) == 0) {
            Item item;
            if (sscanf(line, "ADD %d %63s", &item.id, item.time) == 2) {
                heap_push(item);
            } else {
                printf("ERR invalid add command\n");
                fflush(stdout);
            }
        } else if (strncmp(line, "POP", 3) == 0) {
            heap_pop();
        } else if (strncmp(line, "SNAPSHOT", 8) == 0) {
            print_snapshot();
        } else if (strncmp(line, "STOP", 4) == 0) {
            printf("BYE\n");
            fflush(stdout);
            break;
        } else {
            printf("ERR unknown command\n");
            fflush(stdout);
        }
    }
    return 0;
}
