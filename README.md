# Gorilla CLI

<img src="https://github.com/ShishirPatil/gorilla/blob/gh-pages/assets/img/logo.png" width=20% height=20%>

Gorilla CLI powers your command-line interactions with a user-centric tool. Simply state your objective, and Gorilla CLI will generate potential commands for execution. Gorilla today supports ~1500 APIs, including Kubernetes, AWS, GCP,  Azure, GitHub, Conda, Curl, Sed, and many more. No more recalling intricate CLI arguments! 🦍

Developed by UC Berkeley as a research prototype, Gorilla-CLI prioritizes user control and confidentiality:
 - Commands are executed solely with your explicit approval.
 - While we utilize queries and error logs (stderr) for model enhancement, we NEVER collect output data (stdout).

![gorilla-cli](https://github.com/gorilla-llm/gorilla-cli/assets/30296397/f448c04b-e2a1-4560-b040-37f9840c356d)

## Getting Started

You can readily install Gorilla CLI via pip. 

```bash
pip install gorilla-cli
```

## Usage

Activate Gorilla CLI with `gorilla` followed by your task in plain English.

For instance, to generate a file with 100 random characters, type:

```bash
$ gorilla generate 100 random characters into a file called test.txt
```

or if you prefer, you can use quotes to avoid issues with string parsing:

```bash
$ gorilla "generate 100 random characters into a file called test.txt"
```

Gorilla CLI will then generate candidate commands. Use the arrow keys to navigate through the options, then press enter to execute the chosen command. 

```bash
🦍  Welcome to Gorilla. Use arrows to select
 » cat /dev/urandom | env LC_ALL=C tr -dc 'a-zA-Z0-9' | head -c 100 > test.txt 
   echo $(head /dev/urandom | LC_CTYPE=C tr -dc 'a-zA-Z0-9' | dd bs=100 count=1) > test.txt
   dd if=/dev/urandom bs=1 count=100 of=test.txt
```

Some more examples

```bash
$ gorilla list all my GCP instances
» gcloud compute instances list --format="table(name,zone,status)"
  gcloud compute instances list --format table
  gcloud compute instances list --format="table(name, zone, machineType, status)"
```
```bash
$ gorilla get the image ids of all pods running in all namespaces in kubernetes
» kubectl get pods --all-namespaces -o jsonpath="{..imageID}"
  kubectl get pods --all --namespaces
  kubectl get pod -A -o jsonpath='{range .items[*]}{"\n"}{.metadata.name}{"\t"}{.spec.containers[].image}{"\n"}{end}'
```


## How It Works

Gorilla-CLI fuses the capabilities of various Language Learning Models (LLMs) like [Gorilla LLM](https://github.com/ShishirPatil/gorilla/), OpenAI's GPT-4, Claude v1, and others to present a user-friendly command-line interface. For each user query, we gather responses from all contributing LLMs, filter, sort, and present you with the most relevant options. 

### Arguments

```
usage: go_cli.py [-h] [-p] [command_args ...]

Gorilla CLI Help Doc

positional arguments:
  command_args   Prompt to be inputted to Gorilla

optional arguments:
  -h, --help     show this help message and exit
  -p, --history  Display command history
```

The history feature lets the user go back to previous commands they've executed to re-execute in a similar fashion to terminal history.


## Contributions

We welcome your enhancements to Gorilla CLI! If you have improvements, feel free to submit a pull request on our GitHub page. 

## License

Gorilla CLI operates under the Apache 2.0 license. More details can be found in the LICENSE file. We'd also like to extend our appreciation to [questionary](https://github.com/tmbo/questionary) for their fantastic UI!
