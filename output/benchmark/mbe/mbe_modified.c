#include "/home/bohrok/Documents/DM/lib/insert_criteria/lib/clib/stdio.h"
#include "/home/bohrok/Documents/DM/lib/insert_criteria/lib/clib/stdlib.h"
int p(int j);
int q(int k);
int f1(int k);
int f2(int k);
int f3(int j);
int main(int argc, char *argv[])
{
    int j;
    int k;
    j = (int) strtol(argv[1], NULL, 10);printf("\nORBS:%d:%d:%s:%d\n", 12, 5, "j", j);
    k = (int) strtol(argv[2], NULL, 10);printf("\nORBS:%d:%d:%s:%d\n", 13, 5, "k", k);
    printf("\nORBS:%d:%d:%s:%d\n", 14, 14, "j", j);while (p(j))
    {
        printf("\nORBS:%d:%d:%s:%d\n", 16, 15, "k", k);if (q(k))
        {
            printf("\nORBS:%d:%d:%s:%d\n", 18, 20, "k", k);k = f1(k);printf("\nORBS:%d:%d:%s:%d\n", 18, 13, "k", k);
        }
        else
        {
            printf("\nORBS:%d:%d:%s:%d\n", 22, 20, "k", k);k = f2(k);printf("\nORBS:%d:%d:%s:%d\n", 22, 13, "k", k);
            printf("\nORBS:%d:%d:%s:%d\n", 23, 20, "j", j);j = f3(j);printf("\nORBS:%d:%d:%s:%d\n", 23, 13, "j", j);
        }
    printf("\nORBS:%d:%d:%s:%d\n", 14, 14, "j", j);}
    printf("\nORBS:%d:%d:%s:%d\n", 26, 20, "j", j);printf("%d\n", j);
}
int p(int j)
{
    printf("\nORBS:%d:%d:%s:%d\n", 30, 8, "j", j);if(j > 0)
    {
        return 1;
    }
    else
    {
        return 0;
    }
}
int q(int k)
{
    printf("\nORBS:%d:%d:%s:%d\n", 41, 8, "k", k);if(k < 0)
    {
        return 1;
    }
    return 0;
}
int f1(int k)
{
    printf("\nORBS:%d:%d:%s:%d\n", 49, 12, "k", k);return k + 10;
}
int f2(int k)
{
    printf("\nORBS:%d:%d:%s:%d\n", 53, 12, "k", k);return k - 2;
}
int f3(int j)
{
    printf("\nORBS:%d:%d:%s:%d\n", 57, 12, "j", j);return j - 15;
}
int x(int y)
{
    return 1;
}
