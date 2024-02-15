# group process killer

Kill a process remotely with a keyboard shortcut. Funnily enough, this started as an attempt to cheese the GTA V Criminal mastermind challenge. When you kill the game after any of your teamates die but before the leaderboard shows up, it fails to save the mission progress and you avoid ruining the challenge. The default kill shortcut is left windows + x but can be reconfigured with the -t argument. Uses ngrok internally to tunnel port.

## Installation

```console
pip install git+https://github.com/strny0/group-process-killer
```

## Usage

**As client, run the following command:**

```console
group-process-killer client ws:\\host:port process.exe
```

For example

```console
group-process-killer client ws:\\0.tcp.ngrok.io:12345 GTA5.exe
```

**As server, run the following command:**

```console
group-process-killer server port
```

For example

```console
group-process-killer server 11111
```

Requires you to configure ngrok globally (i.e. have a token in your global config).

NOTE: directinput in gta consumes all keyboard events, we figured out a hack where if you set the keyboard shortcut to `-t "left windows + x"`, you can quickly double press win + x to exit the game. First win + x loses focus of gta by opening a kind of context menu in the start menu. Second press sends input to this program, killing the game.
