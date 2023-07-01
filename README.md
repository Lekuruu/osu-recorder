# osu!recorder

This is a small example project for the [osu.py](https://github.com/Lekuruu/osu.py) python package.
It allows to automatically spectate and save replay files for any osu! player.

Please note that this project was not properly tested and that bugs can occur.
I am also not responsible for anything that can happen to your account.

You can find an example replay [here](https://github.com/Lekuruu/osu-recorder/raw/main/.github/maliszewski%20-%20passchooo%20-%20chooo2023_1%20%5BX%5D%20(2023-07-01%2022-12-01)%20Osu.osr).

## Usage

Install the `osu` package with pip:
```shell
pip install osu
```

```shell
python main.py <id> <username> <password>
```

`id`: Id of the player you want to spectate
`username`: Your bancho username
`password`: Your bancho password

Optional arguments:
`--tourney`: Allow for multiple clients at once (supporter only)
`--out <path>`: Specify the folder where replays get stored (replays)
`--server <url>`: Specify a custom server to use (ppy.sh)
