===========
dTests
===========
A python tool to distributively run GCJ/FB hacker cup testcases on several machines.

How does it work
====================
* First the splitter runs on the input file to split it into seprate test cases.

* Test cases with the actuall code are sent to the server.

* The server distributes the test cases and the actuall code to its registered nodes.

* Each node computes the result for its testcases and sends the result back to the server

* The server collects the results and sort them by their testcase number and sends them back to the calling script.

Installation
============
::

    pip install dTests

Running dTests
==============
* Create new project::

    dtests_job new project_name language

* The only supported languages now are "cpp" and "java".

* Open the new folder and code your splitter to read from the input.in file.

* Between each test cases print "--split--\n". The split marker can be configured in "config.json" file. This will split the input file into single test cases which will be distributed on the machines running.

* Code your program file to read from stdin as if it is reading a single test cases.

* Run the server ::

    dtests_server

* Run one or many nodes on other machines ( or for testing on the same machine )::

    dtests_node --host host --port port

* Finally run the job::

    dtests_job run

* Check the help of these commands for further customizations

Sample project
==================
This is a sample cpp project that takes input and multiply it by itself https://github.com/MohamedBassem/dTests/tree/master/samples/power2

* The config.json file contains the project configuration. The language and the splitter syntax.

* The splitter.cpp file contains the code that reads the input from the "input.in" file and splits it to single test cases.

* The program.cpp file that reads a single test cases from stdin and computes the result.

* To Run this project, run the server and at least one node. Then run "dtests_job run" in the project's directory.

TODO
====
* Finding a way to pass the testcase number to the program

* Writing Tests.

* Making the system fault tolerant.

* Finding a better way for splitting the input file.

* Supporting more programming languages.

For more info visit https://github.com/MohamedBassem/dTests

Contributing
============
Your contributions ( Ideas, improvments, etc.. ) are more than welcome.

LICENSE
=======
Licensed under the `MIT license <https://github.com/MohamedBassem/dTests/blob/master/LICENSE.txt>`_.
