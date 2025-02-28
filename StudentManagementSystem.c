#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define FILENAME "students.dat"

struct Students
{
    int id;
    char name[50];
    int age;
    float marks;
};

void addStudents();
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

        switch (choice)
        {
        case 1:
            addsStudents();
            break;
        case 2:
            displayStudents();
            break;
        case 3:
            searchStudents();
            break;
        case 4:
            deleteStudents();
            break;
        case 5:
            updateStudents();
            break;
        case 6:
            exit(0);
            break;
        default:
            printf("Wrong Choice! Pelese try again.");
        }
        return 0;
    }
}

//Add Student
void addStudents() {
    FILE *fp = fopen(FILENAME,"ab");    // fopen :- automaticaly open a new file
    if(!fp){
        printf("Error Opeening File\n");    // Got this result if we can't find any file
        return;
    }
    struct Students s;
    printf("Enter ID : ");
    scanf("%d",&s.id);
    printf("Enter Name : ");
    scanf("%[^\n]",s.name);
    printf("Enter Age : ");
    scanf("%d",&s.age);
    printf("Enter Marks : ");
    scanf("%d", &s.marks);

    fwrite(&s, sizeof(s), 1, fp);
    printf("Student record added Successfully!\n");
}

//Display Student
void displayStudents(){
    FILE *fp = fopen(FILENAME, "rb");
    if(!fp){
        printf("\nID\tName\tAge\nMarks\n");
        return;
    }

    struct Students s;
    printf("\nID:\tName:\tAge:\tMarks:\n");
    while(fread(&s, sizeof(s), 1, fp))
    {
        printf("%d\t%s\t%d\t%.2f\n", s.id, s.name, s.age, s.marks);
    }
    fclose(fp);
}

// Search Student
void searchStudents() {
    FILE *fp = ffopen(FILENAME, "rb");
    if(!fp) {
        printf("No records found.\n");
        return;
    }
    int id, found = 0;
    struct Students s;
    printf("Enter student ID to search :");
    scanf("%d", &id);
    while(fread(&s, sizeof(s),1,fp)){
        if(s.id == id){
            printf("\nID: %d\nName: %s\nAge: %d\nMarks: %.2f\n", s.id, s.name, s.age, s.marks);
            found = 1;
            break;
        }
    }
    if (!found) 
        printf("Student not found!\n");
        fclose(fp);
}
