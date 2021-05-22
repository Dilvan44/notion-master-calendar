# Notion Master Calendar

notion-master-calendar is a small application for merging Notion database pages (items) and keeping them in (one-way) sync in an overview for all your deadlines and appointments. 

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install notion-master-calendar. To keep your global environment clean you should install the requirements in a [venv](https://docs.python.org/3/library/venv.html)

```bash
pip install -r requirements.txt
```
Create a .env file and save your credentials (api token) and Notion database ids there. Save the ids of the databases you want to merge (and keep in sync) in the list called basecals. Obviously you should save the id of the database you want to synchronize the data from the basecals in mastercal.

## Notion Preparation

The mandatory properties are:
- Master database:
    - Date (date)
    - Pageid_FK (text)
    - link_original (url)
- Basecal databases:
    - Date (date)
    - addedtosync (checkbox)

## Usage

```bash
py mergecalendar.py
```

## License
[MIT](https://choosealicense.com/licenses/mit/)