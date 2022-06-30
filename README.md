# Kimitsu

Sometimes you need to receive sensitive data, but the party that has to send it doesn't know how to securely send it.

Use Kimitsu to generate a unique URL, send to your counterparty, have them set the secret, press save.

Next up simply retrieve the secret via the API, pipe it through to gpg (or whatever) and read the secret.

Kimitsu has no persistent backend other than the filesystem.

Dope.

## How to use Kimitsu Cloud

### TL;DR

On your local machine generate a PGP key. I'm using GnuPG in this example. Commands on your system might be different.
```shell
gpg --quick-generate-key brian@localhost
```

Next up, request a new secret id from Kimitsu, and use that to generate a secret link.
```shell
curl --data "$(gpg --armor --export brian@localhost)" https://kimitsu.xyz/api/secrets | jq -r '.secret_id' | xargs -I {} echo "https://kimitsu.xyz/secrets/{}"
```

Share the resulting link with a friend, e.g `https://kimitsu.xyz/secrets/62bd0e23ce645ce7e3754567a1826bb9a5e5a0ce` and have them fill out the form
with whatever secret they want to share with you.

Once they stored their secret, you can begin retrieving it.

```shell
curl https://kimitsu.xyz/api/secrets/62bd0e23ce645ce7e3754567a1826bb9a5e5a0ce | gpg --decrypt
```

Output:

```shell
gpg: encrypted with 3072-bit RSA key, ID A4C53AC6B1B6AE3A, created 2022-06-30
      "brian@localhost"
Hello Darkness my old friend.
```

### The Long Story

On your local machine generate a PGP key. I'm using GnuPG in this example. Commands on your system might be different.
```shell
gpg --quick-generate-key brian@localhost
```

Next up, request a new secret id from Kimitsu.
```shell
curl --data "$(gpg --armor --export brian@localhost)" https://kimitsu.xyz/api/secrets | jq -r '.secret_id' | xargs -I {} echo "https://kimitsu.xyz/secrets/{}"
```

It looks likes there's a lot going on, so let's walk through it step by step.

First we send our public key to the kimitsu server, requesting a secret id.
```shell
curl --data "$(gpg --armor --export brian@localhost)" https://kimitsu.xyz/api/secrets
```

The return data will look something like this:

```json
{"secret_id":"62bd0ce30d412ce4b0ef42faab906385d1a85fbb"}
```

We pipe `|` this to jq, which is a json parser, to extract the secret ID from the json. 
The `-r` means we ask `jq` to return the data unquoted.

```shell
jq -r '.secret_id'
```

This return data will be, if all goes well, a string that looks like this: `62bd0e16a4ae969c0b534f19b3af1edc32ce926f`.

Now we finally pipe this through `xargs` which will basically allow us to use the output from the previous command in a new command.

```shell
xargs -I {} echo "https://kimitsu.xyz/secrets/{}"
```

In this case we take the output from `62bd0e16a4ae969c0b534f19b3af1edc32ce926f` and use that to construct the secret url.

The output will look something like this: `https://kimitsu.xyz/secrets/62bd0e23ce645ce7e3754567a1826bb9a5e5a0ce`

Send this link to your friend, have them store whatever secret they wish. 

Once they stored their secret, you can retrieve and decode it with the following command:

```shell
curl https://kimitsu.xyz/api/secrets/62bd0e23ce645ce7e3754567a1826bb9a5e5a0ce | gpg --decrypt
```

The output, depending on the contents, should look something like this:

```shell
gpg: encrypted with 3072-bit RSA key, ID A4C53AC6B1B6AE3A, created 2022-06-30
      "brian@localhost"
Hello Darkness my old friend.%
```

## How to install

* Make sure gpg installed locally.
* Clone this repository.
* `pip install -r requirements.txt`

## How to run Kimitsu

Read up on Flask's [documentation](https://flask.palletsprojects.com/en/2.1.x/tutorial/deploy/).

Don't forget to set the `BASE_PATH` to where you want to store your secrets. (e.g `/data/kimitsu`)

Use a reverse proxy to prevent people from sending you massive files.