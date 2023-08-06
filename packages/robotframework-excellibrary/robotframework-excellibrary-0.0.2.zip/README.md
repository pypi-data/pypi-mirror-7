robotframework-excellibrary for Robot Framework
==================================================


Introduction
------------

Robotframework-excellibrary is a Robot Framework Library that provides keywords to allow opening, reading, writing and saving Excel files. The robotframework-excellibrary leverages two other python libraries [xlutils](https://pypi.python.org/pypi/xlutils/1.7.1) and [natsort](https://pypi.python.org/pypi/natsort/3.3.0). Xlutils installs [xlrd](https://pypi.python.org/pypi/xlrd) that reads data from an Excel file and [xlwt](https://pypi.python.org/pypi/xlwt) that can write to an Excel file.


- Information about robotframework-excellibrary keywords can be found on the [ExcelLibrary-Keyword Documentation](http://navinet.github.io/robotframework-excellibrary/ExcelLibrary-KeywordDocumentation.html) page.
- Information about working with Excel files in Python can be found on the [Python Excel](http://www.python-excel.org/) page.
- Useful pdf for practical use with Excel files [here](http://www.simplistix.co.uk/presentations/python-excel.pdf).


Requirements
------------
* Python 2.7.4 (Newer versions not tested)
* Robot Framework 2.8.5 (Newer versions not tested)
* xlutils 1.7.1 (Newer versions not tested). Access the downloads [here](https://pypi.python.org/pypi/xlutils/1.7.1), or use pip install xlutils.
* natsort 3.3.0 (Newer versions not tested). Access the downloads [here](https://pypi.python.org/pypi/natsort/3.3.0), or use pip install natsort.


Installation
------------
#### Using pip ####

The recommended installation tool is [pip](http://pip-installer.org).

Install pip.
Enter the following:

    pip install robotframework-excellibrary

Append ``--upgrade`` to update both the library and all 
its dependencies to the latest version:

    pip install --upgrade robotframework-excellibrary

To install a specific version enter:

    pip install robotframework-excellibrary==(DesiredVersion)

#### Manual Installation ####

To install robotframework-excellibrary manually, install all dependency libraries before installing robotframework-excellibrary.

1) Install [Robot Framework installed](http://code.google.com/p/robotframework/wiki/Installation).

2) Download source distributions (``*.tar.gz`` / ``*.zip``) for the library and its
   dependencies.

  robotframework-excellibrary and dependencies:

   - [https://pypi.python.org/pypi/robotframework-excellibrary](https://pypi.python.org/pypi/robotframework-excellibrary)
   - [https://pypi.python.org/pypi/xlutils/1.7.1](https://pypi.python.org/pypi/xlutils/1.7.1)
   - [https://pypi.python.org/pypi/natsort/3.3.0](https://pypi.python.org/pypi/natsort/3.3.0)

3) Extract each source distribution to a temporary location using 7zip (or your preferred zip program).

4) Open command line and go to each directory that was created from extraction and install each project using:

       python setup.py install

#### Uninstall ####

To uninstall robotframework-excellibrary use the following pip command: 

    pip uninstall robotframework-excellibrary

However, if the package was installed manually it will need to be uninstalled manually:

1) Navigate to ``C:\Python27\ExcelRobotTest`` and delete ExcelRobotTest.txt,  and ExcelLibrary-KeywordDocumentation.html

2) Navigate to ``C:\Python27\Lib\site-packages`` and delete robotframework-excellibrary-0.0.2-py2.7.egg-info and the folder ``robotframework-excellibrary``

Directory Layout
----------------

*ExcelLibrary/ExcelLibrary.py* :
    The Robot Python Library that makes use of the xlutils and natsort.

*Tests/acceptance/ExcelRobotTest.txt* :
    Example test file to display what various keywords from robotframework-excellibrary accomplish

*doc/ExcelLibrary-KeywordDocumentation.html* :
    Keyword documentation for the robotframework-excellibrary.


Usage
-----

To write tests with Robot Framework and robotframework-excellibrary, 
ExcelLibrary must be imported into your Robot test suite.
See [Robot Framework User Guide](http://code.google.com/p/robotframework/wiki/UserGuide) for more information.


Running the Demo
----------------

The test file ExcelRobotTest.txt, is an easily executable test for Robot Framework using robotframework-excellibrary. 
For in depth detail on how the keywords function, read the Keyword documentation found here : [Keyword Documentation](http://navinet.github.io/robotframework-excellibrary/ExcelLibrary-KeywordDocumentation.html)

To run the test navigate to the Tests directory in C:\Python folder. Open a command prompt within the *Tests/acceptance* folder and run:

    pybot ExcelRobotTest.txt


Things to Note When Using robotframework-excellibrary
-----------------------------------

* When using the keyword *Add New Sheet* the user cannot perform any functions before or after this keyword on the currently open workbook. The changes that other
keywords make will not be saved when the keyword *Add New Sheet* is used. They must add a sheet then save the workbook before using any other keyword.
If they want to use any other keywords on the workbbok they must open the workbook again to do so.
* We cannot use xlsx files as this has not been implemented in the xlrd library. Further information can be [found here](http://stackoverflow.com/questions/13892307/python-xlutils-formatting-info-true-not-yet-implemented) and discussed [here](https://groups.google.com/forum/#!msg/python-excel/w2AoQkX3TZc/1qjT1KzwoUsJ). To get round this issue, the user can save the excel files with the xls extension, this is a Microsoft Excel 97-2003 Worksheet.


Getting Help
------------
The [user group for Robot Framework](http://groups.google.com/group/robotframework-users) is the best place to get help. Include in the post:

- Contact the [Python-Excel google group](https://groups.google.com/forum/#!forum/python-excel)
- Full description of what you are trying to do and expected outcome
- Version number of robotframework-excellibrary and Robot Framework
- Traceback or other debug output containing error information