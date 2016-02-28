# Drip

```
# setup environment
pip install -r requirements.txt

# install data
python -m spacy.en.download

# setup NLP data
python setup/data.py

# create databases
./setup/db create

# setup initial sources/feeds
python setup/sources.py

# add cron job (adjust as needed)
crontab -e
*/20 * * * * cd ~/projects/drip; ~/env/drip/bin/python3 collect.py
```

Some convenience commands:

```
# manually collect new articles
python d.py update

# remove duplicate articles
# (articles with the same title are considered duplicates)
python d.py remove_duplicates

# count the articles, events, and stories
python d.py count

# preview the events and stories
python d.py preview

# run the api
python d.py api
```

drip is still under active development.

---

There is a very simple API available to develop against.

Run the API server and the following endpoints are available:

- `/events` - the latest 50 events
- `/stories` - the latest 50 stories
- `/events/<id>` - a single event