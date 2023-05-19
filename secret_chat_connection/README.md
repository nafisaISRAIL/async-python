# Secret chat.
An example of communication between a client and a server using an asynchronous socket.

## Description

The project has two files **sender.py** and **reader.py**.

#### Reader
The reader.py connects to provided host and port and saves incoming data to the file.

```bash
python3 reader.py --host some.host.or.ipaddress \
--port PORT --history path/to/save_file.txt
```


The _host_, _port_ and _history_" arguments are not required to start the program. By default "host" is set to "minechat.dvmn.org", "post" to 5000, and "history" to a local directory. 


#### Sender
The sender.py connects to the provided host and sends a message. 

```bash
python3 sender.py --message "Hello, World!" --host some.host.or.ipaddress \
--port PORT  --nickaname "Devman"

```

For sender.py the _**message**_ argument is mandatory.
The _host_, _port_, and _nickname_ arguments are not required to start the program. By default "host" is set to "minechat.dvmn.org", "post" to 5050, and "nickname" could be empty.

# Requirements
Program is running with >= python3.7. Asyncio library is built-in but library **aiofiles** must be installed in the environment of the program running. 

