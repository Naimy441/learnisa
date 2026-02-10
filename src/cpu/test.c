int exit_code = 0 + 1 * -3;

int random(int a, int b, int c) {
    int sum = 0;
    while (a < b) {
        sum = sum + (c + 1 * 3) / 3;
        a = a + 1;
    }
    return sum;
}

int random2(int a, int b, int c) {
    int sum = 0;
    for (int i = a; i < b; i = i + 1) {
        sum = sum + (c + 1 * 3) / 3;
    }
    return sum;
}

int main() {
    int num1 = random(2, 5, 3);
    if (num1 == random2(2, 5, 3)) {
        exit_code = 1;
    } else if (num1 != 15) {
        exit_code = 3;
    } else {
        exit_code = 2;
    }
}