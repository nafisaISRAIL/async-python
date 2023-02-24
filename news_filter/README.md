# Jaundiced news filter

The project filters articles from news portals for "yellowness. Requests are sent to the server as a query parameter, in response comes the article's score and processing status. 
# How to install

You will need Python version 3.7 or later. It is recommended that you create a virtual environment to install packages.

The first step is to install the packages:

```python3
pip install -r requirements.txt
```

# How to run

```python3
python server.py
```

# How to use

In your browser open the new tab and type 
```
http://localhost:8080/?urls=https://inosmi.ru/economic/20190629/245384784.html,https://inosmi.ru/economic/20190629/245384784.html
```
Currently the program works with articles taken from https://inosmi.ru site.
If not any url was provided the error will be displayed on the screen.

# How to run tests

For testing [pytest](https://docs.pytest.org/en/latest/) is used, the tests cover code fragments difficult to debug: text_tools.py, adapters and processor. Commands to run tests:

```
python -m pytest adapters/inosmi_ru.py
```

```
python -m pytest text_tools.py
```

```
python -m pytest text_tools.py
```

```
python -m pytest test_processor.py
```
