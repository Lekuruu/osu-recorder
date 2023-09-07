# osu!recorder

This is a small example project for the [osu.py](https://github.com/Lekuruu/osu.py) python package.
It allows you to automatically record and save replay files for any player that is currently online, by spectating them.

Please note that this project was not properly tested and that bugs can occur.
I am also not responsible for anything that can happen to your account.

You can find an example replay [here](https://github.com/Lekuruu/osu-recorder/blob/main/.github/BlackDog5%20-%20Katy%20Perry%20-%20Hot%20N%20Cold%20%5BRoller%20Coaster%20v2%5D%20(2023-09-05%2020-29-24)%20Osu.osr).

## Usage

Install the `osu` package with pip:

```shell
pip install osu
```

```shell
python main.py <id> <username> <password>
```

- `id`: Id of the player you want to spectate
- `username`: Your bancho username
- `password`: Your bancho password

Optional arguments:

- `--tourney`: Allow for multiple clients at once (supporter only)
- `--out <path>`: Specify the folder where replays get stored (replays)
- `--server <url>`: Specify a custom server to use (ppy.sh)
