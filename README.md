ECroPS (Engine for Crop Parallelizable Simulations) is a software platform to build and run agronomic models. It was developed by JRC, Unit D5.

For all the documentation, please read the [manual](./ecrops/Manual.md) under the ecrops folder.

----

This installation comes with a test console application (EcropsWofostExampleConsole folder), that reads some test data and runs a single simulation on it. It could be used to verify the installation of the package and to familiarize to it.

To test the EcropsWofostExampleConsole application in docker environment, go to the root folder (where this file is) and run

docker build -t ecrops-test-application .

docker run ecrops-test-application

----

To test the EcropsWofostExampleConsole application using a Python virtual environment (`venv` package), go to any folder of the file system and run

`python -m venv ecrops_venv` 
where ecrops_venv is the name to assign to the virtual enviroment

The folder `ecrops_venv` will be created.

Activate the virtual environment by running

`ecrops_venv\Scripts\activate`

Once activated, your terminal will show the virtual environment's name in the prompt. Then, from the prompt, install the ecrops package by running

`python -m pip install /path/to/ecrops/setup/file`

(for example, if you cloned ecrops in the folder C:\ecrops_folder, you run the command `python -m pip install C:\ecrops_folder\ecrops\ecrops`

This will install ecrops and all the dependencies in the virtual environment. 

Finally, launch the EcropsWofostExampleConsole script by moving to the folder where the console is and running the main file

`cd /path/to/EcropsWofostExampleConsole`
`python /path/to/EcropsWofostExampleConsole/main.py`
