## 📌 Overview

Our primary goal today is to use PyEZ to provision eight Juniper vMX routers into various elements of an MPLS network.

While PyEZ has the capability of pushing individual lines, or groups of lines, of configurations to a device, here we will be building and pushing an entire configuration.

We will also be following the guiding principles of [Infrastructure-as-Code]("https://en.wikipedia.org/wiki/Infrastructure_as_code"), where we will store our the elements of our configuration as YAML, to be ran through a Jinja2 template to output our configurations.

---

## 🐍 Files

All of our project's scripts, variables, and template files are stored within the [files/python](https://github.com/cdot65/juniper-mpls-l3vpn-demo/tree/main/files/python) directory.

```bash
files/python
├── configurations/
├── templates/
├── tests/
├── vars/
├── configure.py
├── download.py
├── generate.py
├── inventory.yaml
├── rollback.py
└── validate.py
```

### Python Scripts

You likely don't need me to explain that the files that end with `.py` are the various Python scripts. Here is a quick glimpse into the four provided.

| Script         | Action                                              |
| -------------- | --------------------------------------------------- |
| `generate.py`  | Build the configurations locally with Jinaj2.       |
| `configure.py` | Build and push our configurations with PyEZ.        |
| `download.py`  | Download our configurations with PyEZ.              |
| `rollback.py`  | Rollback to our bootstrap configurations with PyEZ. |
| `validate.py`  | Validate our MPLS L3VPN circuit with JSNAPy.        |

### Inventory file

The `inventory.yaml` file stores information about our devices, basic information like hostname and IP address.

### `configurations/` directory

If you choose to generate the configurations locally but _not_ push them to the devices, then you will find the generated configurations within the `configurations` directory. I had also included the working final configurations in this directory if you just want to see the resulting configurations.

### `templates/` directory

Since we are storing our configuration as code, we will need some kind of templating engine to run our variables through to produce the configurations. For this we have Jinja2 to handle the templating, and its template files are stored in the `templates` directory.

### `vars/` directory

Finally, the device's configuration will be stored as YAML files found within the `vars/` directory. Each device will have its own file to represent its configuration. We will run these files through the Jinaj2 templates to produce our configurations.

---

## 🛠️ Tools

In hopes to making this project as easy as possible to execute, I have provided many tools to help with execution of the tasks within this project.

### Poetry

A [Poetry](https://python-poetry.org/docs/) lock file to help you create a Python environment that mirrors my own. As long as you [have Poetry installed on your machine](https://python-poetry.org/docs/), to you can simply type `poetry install` to create the virtual environment, followed by `poetry shell` to activate it.

### Invoke

You will find a packaged called [Invoke](http://www.pyinvoke.org/) installed within the virtual environment. Invoke is an elegant way to create CLI shortcuts for commands that are long to type out. Here is a short list of some of the Invoke operations created in the `tasks.py` file.

| Command            | Action                                              |
| ------------------ | --------------------------------------------------- |
| `invoke generate`  | Build the configurations locally with Jinaj2.       |
| `invoke configure` | Build and push our configurations with PyEZ.        |
| `invoke download`  | Download our configurations with PyEZ.              |
| `invoke rollback`  | Rollback to our bootstrap configurations with PyEZ. |
| `invoke validate`  | Validate our MPLS L3VPN circuit with JSNAPy.        |

### Dockerfile

A Dockerfile has also been provided for those that would like to execute this within an isolated container instead of a virtual environment. A couple of additional Invoke tasks are listed below to help with building and accessing the Docker container environment.

| Command        | Action                                                   |
| -------------- | -------------------------------------------------------- |
| `invoke build` | Build an instance of the Docker container image locally. |
| `invoke shell` | Get access to the BASH shell within our container.       |

---

## 🚀 Workflow

The workflow will look like this:

1. Have Poetry install your Python packages in a virtual environment (one-time operation)
2. Activate your new virtual environment with Poetry
3. Run locally or within a container using the Invoke package

```bash
poetry install
poetry shell
invoke configure
```