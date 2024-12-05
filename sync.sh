rsync -av --exclude 'venv/' \
         --exclude '__pycache__/' \
         --exclude '*.pyc' \
         --exclude '.git/' \
         --exclude '.env' \
         --exclude '*.tar' \
         ./ ticki:/home/pi/ticki/
