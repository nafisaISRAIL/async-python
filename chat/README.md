# Secret chat

Desktop application which uses asynchronous socket connection to send and get messages.

## Description

The project has file **main.py**  as an entrypoint of the project. 

## Prerequisites
To start and run this application tkinter package and required libraries from requirements.txt file should be installed to working environment. 
Create a virtual environment and installs the project dependencies into it. 
Run the following command from the base directory of the project:
1. Create virtual environment:
    ```bash
    python3.8 -m venv env
    ```
2. Activate the virtualenv:
    ```bash
    source env/bin/activate
    ```
3. Install dependencies:
    ```bash 
    pip install -r requirements.txt
    ```

Create a .env file in working directory and set mandatory parameters to run the application. (.env.example)

If you have an auth token just set it as a value of MINECHAT_TOKEN variable in .env file. 

Run the application:
    ```bash
    python3 main.py
    ```

Also main.py can be run with commandline arguments

    ```bash
    python3 main.py --host HOST --read-port READ_PORT --write-port WRITE_PORT --token TOKEN --history HISTORY.txt
    ```

##### Description
All messages are saved in a file histroy.txt, which will be displayed when the program is restarted.