#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
bool p(int i);
bool q(int c);
int h(int i);
int f();
int g();
int main(int argc, char *argv[])
{
    int i;
    int c;
    int x;
    i = atoi(argv[1]);printf("\nORBS:%d:%d:%s:%d\n", 14, 5, "i", i);
    c = atoi(argv[2]);printf("\nORBS:%d:%d:%s:%d\n", 15, 5, "c", c);
    x = atoi(argv[3]);printf("\nORBS:%d:%d:%s:%d\n", 16, 5, "x", x);
    printf("\nORBS:%d:%d:%s:%d\n", 17, 14, "i", i);while (p(i))
    {
        printf("\nORBS:%d:%d:%s:%d\n", 19, 15, "c", c);if (q(c))
        {
            x = f();printf("\nORBS:%d:%d:%s:%d\n", 21, 13, "x", x);
            c = g();printf("\nORBS:%d:%d:%s:%d\n", 22, 13, "c", c);
        }
        printf("\nORBS:%d:%d:%s:%d\n", 24, 15, "i", i);i = h(i);printf("\nORBS:%d:%d:%s:%d\n", 24, 9, "i", i);
    printf("\nORBS:%d:%d:%s:%d\n", 17, 14, "i", i);}
    printf("\nORBS:%d:%d:%s:%d\n", 26, 20, "x", x);printf("%d\n", x);  
}
bool p(int i)
{
    printf("\nORBS:%d:%d:%s:%d\n", 30, 9, "i", i);if (i > 0)
    {
        return true;
    }
    else
    {
        return false;
    }
}
bool q(int i)
{
    printf("\nORBS:%d:%d:%s:%d\n", 41, 9, "i", i);if (i < 0)
    {
        return true;
    }
    else
    {
        return false;
    }
}
int h(int i)
{
    printf("\nORBS:%d:%d:%s:%d\n", 52, 12, "i", i);return i - 1;
}
int f()
{
    return -100;
}
int g()
{
    return 100;
}