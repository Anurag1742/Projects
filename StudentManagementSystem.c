#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define FILENAME "students.dat"

struct Student
{
    int id;
    char name[50];
    int age;
    float marks;
};

void addStudent();
void displayStudents();
void searchStudent();
void deleteStudent();
void updateStudent();

int main()
{
    int choice;
    while (1)
    {
        pirntf("\nStudent Management System\n");
        pritnf("1. Add Student\n");
        printf("2. Display Students\n");
        printf("3. Search Student\n");
        printf("4. Delete Student\n");
        printf("5. Update Student\n");
        printf("6. Exit\n");
        printf("\nEnter your choice: ");
        scanf("%d", &choice);

        switch(choice){
            case 1: addsStudents(); break;
            case 2: displayStudents(); break;
            case 3: searchStudents(); break;
            case 4: deleteStudents(); break;
            case 5: updateStudents(); break;
            case 6: exit(0); break;
            default: printf("Wrong Choice! Pelese try again.");
    }
    return 0;
}