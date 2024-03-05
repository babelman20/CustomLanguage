#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>

int main(int argc, char * argv[]) {
  if (argc != 2) {
    printf("Wrong number of args, must be 2\n");
    return 1;
  }

  //string compileFile(argv[1]);
  int fd = open(argv[1], O_RDONLY);

  char * line = (char*) malloc(256);
  int readCt = read(fd, line, 255);
  line[readCt] = 0;

  int newlineIndex = 0;
  for (; newlineIndex < readCt; newlineIndex++) {
    char c = line[newlineIndex];
    if (c == 0) break;
    printf("%c", c);
    if (c == '\n') break;
  }

  lseek(fd, newlineIndex+1, SEEK_SET);
  readCt = read(fd, line, 255);
  line[readCt] = 0;
  printf("%s", line);
  printf("\n");

  return 0;
}
