## dTests

A python tool to distributively run GCJ/FB hacker cup testcases on several machines.

### How does it work
- First the splitter runs on the input file to split it into seprate test cases.
- Test cases with the actuall code is sent to the server.
- The server distributes the test cases and the actuall code to its registered nodes.
- Each node computes the result for its testcases and sends the result back to the server
- The server collects the results and sort them by their testcase number and sends them back to the calling script.

### Running dTests
SOON

### TODO
- Finding a way to pass the testcase number to the program
- Writing Tests.
- Making the system fault tolerant.
- Finding a better way for splitting the input file.
- Supporting more programming languages.


