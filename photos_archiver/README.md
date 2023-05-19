# Microservice for downloading archived files

The microservice assists the main CMS website and handles requests for downloading archives with files. Microservice can do nothing but pack files into an archive. The files are uploaded to the server via FTP or the CMS admin panel.

The archive is created "on the fly" on request from the user. The archive is not saved to disk, instead, it is immediately sent to the user for download as it is packed.

The archive is protected from unauthorized access by a hash in the download link address, e.g.: `http://host.ru/archive/3bea29ccabbbf64bdebcc055319c5745/`. The hash is set by the name of the directory with the files, the directory structure looks like this
```
- photos
    - 3bea29ccabbbf64bdebcc055319c5745
      - 1.jpg
      - 2.jpg
      - 3.jpg
    - af1ad8c76fda2e48ea9aed2937e972ea
      - 1.jpg
      - 2.jpg
```


## Getting started with Docker

If you don't already have Docker installed, [get it here](https://www.docker.com/get-started).

```bash
docker-compose run --rm archiver
```

## To start the server independently, run:

```bash
docker-compose up archiver
```

### Not mandatory environment variables

- SHOW_LOGS - should be logs displayed in standard stdout and stderr or not.
- PHOTOS_DIR - the absolute path of the photos folder.
- PAUSE_TIME - the delay time between sending chunks of the file.


You can test to see if the server is running correctly by visiting http://localhost:8080/ in your favorite browser.
Send requests to the path `/archive/` to download archived files:

```
GET http://host.ru/archive/3bea29ccabbbf64bdebcc055319c5745/
GET http://host.ru/archive/af1ad8c76fda2e48ea9aed2937e972ea/
```