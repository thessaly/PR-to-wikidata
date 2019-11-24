# prtowikidata
A bot to receive Pull Request events from GitHub and update WikiData


## Usage

To run the app use flask or gunicorn:

```
flask run
```

```
gunicorn app:app
```


## Expose local server

To test this app, run it locally and expose it to the internet using a service like ngrok or localtunnel:

```
lt --port 5000 --subdomain hello-world-1337
```

This exposes the localhost port 5000 to https://hello-world-1337.localtunnel.me

Make sure this URL is configured as webhook URL on your GitHub repository (for the `push` event).
