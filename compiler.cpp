#include <iostream>
#include <string>
#include <unistd.h>

using namespace std;

int main(int argc, char * argv[]) {
  if (argc != 2) {
    cout << "Wrong number of args, must be 2" << endl;
    return EXIT_FAILURE;
  }

  //string compileFile(argv[1]);
  int fd = open(argv[1], O_RDONLY);

  char * line = (char*) malloc(256);
  int readCt = read(fd, line, 255);

  int newlineIndex = 0;
  for (; newlineIndex < readCt; newlineIndex++) {
    if (c == 0) break;
    cout << c;
    if (c == '\n') break;
  }

  lseek(fd, newlineIndex, SEEK_SET);
  readCt = read(fd, line, 255);
  cout << line << endl;

  return EXIT_SUCCESS;
}
