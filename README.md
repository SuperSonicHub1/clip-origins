# Clip Origins

Use Twitch's GraphQL API in order to find all the clips a VOD is associated with.

The tool allows one to view the clips in chronological or
popular (most views on top) order.

## Install
```bash
poetry install
# For the lazy...
python3 main.py 
# For the more upstanding
gunicorn 'clip_origins:create_app()'
```
