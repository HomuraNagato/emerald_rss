
# call python script to access web pages
#python emerald_rss.py

# sync emerald_rss content into videos directory
# rsync [options] [source] [destination]
# -a =archive mode (recurses, perserves groups and owners; great for backups)
# -v = verbose
# -z = compress data during transfer
# -h = if P, then show in human readable format
# -P = show partial progress during tranfer
# --dry-run = show what rsync would do without actually performing the action
# -e 'ssh -p 2222' use port 2222 of remote device
# --no-perms for connecting to unsecure device such as android phone
rsync -avzhP --remove-source-files /home/nagato/moonPrism/emerald_rss/westminster_hour/ /mnt/c/Users/Nagato/Music/iTunes/iTunes\ Media/Automatically\ Add\ to\ iTunes
rsync -avzhP --remove-source-files /home/nagato/moonPrism/emerald_rss/marketplace/ /mnt/c/Users/Nagato/Music/iTunes/iTunes\ Media/Automatically\ Add\ to\ iTunes


