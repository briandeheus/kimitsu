# Kimitsu

Sometimes you need to receive sensitive data, but the party that has to send it doesn't know how to securely send it.

Use Kimitsu to generate a unique URL, send to your counterparty, have them set the secret, press save.

Next up simply retrieve the secret via the API, pipe it through to gpg (or whatever) and read the secret.

Kimitsu has no persistent backend other than the filesystem.

Dope.

## How to install

* Make sure gpg installed locally.
* Clone this repository.
* `pip install -r requirements.txt`

## How to run Kimitsu

Read up on Flask's [documentation](https://flask.palletsprojects.com/en/2.1.x/tutorial/deploy/).

Don't forget to set the `BASE_PATH` to where you want to store your secrets. (e.g `/data/kimitsu`)

Use a reverse proxy to prevent people from sending you massive files.