# Gorilla CLI

Gorilla CLI revolutionizes your command-line interactions with a user-centric tool that understands natural language commands. Simply state your objective, and Gorilla CLI will generate potential commands for execution. No more need to recall intricate command-line arguments!

Developed by UC Berkeley as a research prototype, Gorilla-CLI prioritizes user control and confidentiality:
 - Commands are executed solely with your explicit approval.
 - While we utilize queries and error logs (stderr) for model enhancement, we NEVER collect output data (stdout).

## Getting Started

You can readily install Gorilla CLI via pip. 

```bash
pip install gorilla-cli
```

## Usage

Activate Gorilla CLI with a straightforward `gorilla` followed by your command in plain English.

For instance, to list all files in the current directory, type:

```bash
$ gorilla I want to list all files in the current directory
```

or if you prefer, you can use quotes to avoid issues with string parsing:

```bash
$ gorilla "I want to list all files in the current directory" 
```

Gorilla CLI will then generate potential commands. Simply use the arrow keys to navigate through the options, then press enter to execute the chosen command. 

```
🦍  Welcome to Gorilla. Use arrows to select
 » ls
   ls -l
   ls -al
```

Some more examples

```bash
$ gorilla list all my GCP instances
» gcloud compute instances list --format="table(name,zone,status)"
  gcloud compute instances list --format table
  gcloud compute instances list --format="table(name, zone, machineType, status
```
```bash
$ get the image ids of all pods running in all namespaces in kubernetes
» kubectl get pods --all-namespaces -o jsonpath="{..imageID}"
  kubectl get pods --all --namespaces
  kubectl get pod -A -o jsonpath='{range .items[*]}{"\n"}{.metadata.name}{"\t"}{.spec.containers[].image}{"\n"}{end}'
```


## How It Works

Gorilla-CLI fuses the capabilities of various Language Learning Models (LLMs) like [Gorilla LLM](https://github.com/ShishirPatil/gorilla/), OpenAI's GPT-4, Claude v1, and others to present a user-friendly command-line interface. For each user query, we gather responses from all contributing LLMs, filter, sort, and present you with the most relevant options. 

## Contributions

We welcome your enhancements to Gorilla CLI! If you have improvements, feel free to submit a pull request on our GitHub page. 

## License

Gorilla CLI operates under the Apache 2.0 license. More details can be found in the LICENSE file. We'd also like to extend our appreciation to [questionary](https://github.com/tmbo/questionary) for their fantastic UI!
