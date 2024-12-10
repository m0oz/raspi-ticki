rsync -av --filter=":- .gitignore" \
         --exclude=".git/" \
         ./ ticki:/home/pi/ticki/
rsync -av ./mp3/ ticki:/home/pi/ticki/mp3/

