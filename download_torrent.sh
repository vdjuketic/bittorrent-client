read -p "Which torrent do you want to download ? " torrent

printf "\n"


cd app
python3 main.py download -o /tmp/test.txt /mnt/s/Projects/CodeCrafters/codecrafters-bittorrent-python/torrents/$torrent