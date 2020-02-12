# ✨ update.sh

Automates updating the WebApp:
    - prepares data based on the data in the Azure Usage dump one drive directory 
    - builds and publishes container with the new data

### Setting up a script to update the WebApp automatically on MacOS

🛎️ In order to make this approach work `$HOME/.docker/config.json` should not contain "credsStore": "osxkeychain"

Then,
- .bash_profile needs to have `$DOCKER_USER` and `$DOCKER_PASSWORD` set.

- add a new cron job:

```{bash}
env EDITOR=nano crontab -e
```

Add lines similar to:

```
00 12 * * * /Users/tlazauskas/git/Turing/Azure_usage/utils/update.sh
00 17 * * * /Users/tlazauskas/git/Turing/Azure_usage/utils/update.sh

```

Where
```
* * * * *  command to execute
│ │ │ │ │
│ │ │ │ └─── day of week (0 - 6) (0 to 6 are Sunday to Saturday, or use names; 7 is Sunday, the same as 0)
│ │ │ └──────── month (1 - 12)
│ │ └───────────── day of month (1 - 31)
│ └────────────────── hour (0 - 23)
└─────────────────────── min (0 - 59)
```

Useful commands:

`crontab -l` - list all the cron jobs

`crontab -r` - removes all the cron jobs

