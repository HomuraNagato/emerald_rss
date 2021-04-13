
# Emerald RSS

Program simulates an RSS feed by creating a connection to a website and using beautiful soup to
locate media on the site, where traversal of the page is page dependant. Running the program will
be prompted with one of the choices below. Follow the prompt to select. Once a connection is
established, another prompt for which media to download will appear. Once selected, the media
will be downloaded to a directory of the same name as the chosen site.


## Westminster Hour

Download programs from the BBC's Westminster Hour, found at the site: https://www.bbc.co.uk/programmes/p02nrs6c/episodes/downloads.
Content is at the highest 128kbps offered.

## Marketplace

Download programs from NPR's Marketplace, found at the site: https://feeds.publicradio.org/public_feeds/marketplace-pm/rss/rss.

### preferences

Adjust configs/preferences.yaml for custom number of items to display and number of threads. See comments in emerald_rss.py - load_prefs function for further details.

## logs

### 2021.04.13

Added multithreading!

### 2019.03.07

First push to github!