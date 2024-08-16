# Kaniko Tool ⚡

## Get the tool ⬇️
Download it from [here](https://github.com/angad-k/kanikotool/releases)

## Usage ⏯️
Example:
`python .\kanikotool.pyz deploy --project .\Newfolder\ --imagename kambli`
Here,
- Python version should be 3.x
- `--project` is optional. If not passed, tool shall assume `.` to be the project directory.
- `--imagename` is required. This is the name that uploaded image will have.

### Requirements :dependabot:

- Run this command once, to get the dependencies ready: `pip install kubernetes click`
- This tool assumes that you have a minikube cluster running.
- Python :)
- The Dockerfile should be somewhere inside the project directory. The tool will find it automatically.

## How auth credentials are managed 🔐

The tool makes a kubernetes secret and uses it to mount the credentials onto the kaniko pod. The secret is mounted as `config.json` that the kaniko pod expects.
