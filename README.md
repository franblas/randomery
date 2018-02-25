# Randomery &#9861;
Random links from the web

## Requirements
- Python 2.7.x: `python --version`
- [Install pip](https://pip.pypa.io/en/stable/installing/)
- [Download PhantomJS driver binary](http://phantomjs.org/download.html) (regarding your os) and put it at the root of the project as `phantomjs`
- Install python packages
```bash
pip install virtualenv
virtualenv venv
source venv/bin/activate # . venv/bin/activate
pip install -r requirements.txt
```
- Download unwanted urls list (used to filter links)
```bash
wget http://sbc.io/hosts/alternates/fakenews-gambling-porn/hosts > unwanted_urls
```

## Configure the server
Put the configuration into `config.json` file with the following format
```json
{
  "PORT": 4000,
  "APP_SECRET_KEY": "abcd1234",
  "WEBSITE_TITLE": "MyWebsite",
  "MONGO_URI": "mongodb://localhost:27017",
  "feeder": {
    "PHANTOM_JS_DRIVER_ARGS": ["--web-security=no", "--ssl-protocol=any", "--ignore-ssl-errors=yes"],
    "PAGE_LOAD_TIMEOUT": 120,
    "DEFAULT_USERNAME": "randomery",
    "MOBILE_USER_AGENT": "Mozilla/5.0 (Linux; Android 7.1.2; Nexus 5X Build/N2G48C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.98 Mobile Safari/537.36",
    "DESKTOP_USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
  }
}
```

## Run dev
```bash
mkdir -pv mongodb/data # create data folder
mongod --dbpath mongodb/data # start the db
python server.py # start the server
```

## Run prod
### Run locally
```bash
mkdir -pv mongodb/data # create data folder
mongod --dbpath mongodb/data # start the db
uwsgi -H venv --ini uwsgi.ini # start the server
```

### Run on a server
```bash
mkdir -pv /mongodb/data # create data folder
pip install supervisor
# TODO
```

## Feed the database with RSS
Put some rss links into `rss_sources.json` file with the following format
```json
{
  "sources": [
    "https://example.com/rsslink",
    "https://example2.com/othersslink"
  ]
}
```

Run the feeder
```bash
python -c "from lib.feeder import insert_all_links;insert_all_links()"
```

## Workers
Process links added by users (:warning: infinite loop)
```bash
python -c "from lib.worker import job_loop;job_loop()"
```

## Linter
Spot some issues, bad typos or bad indentation
```bash
pip install pylint # install
pylint lib server.py # run
```

## PhantomJS drivers issues
Some of them can still run even after stopping the application, just kill them
```bash
kill -9 $(ps aux | grep phantomjs | awk '{print $2}')
```
