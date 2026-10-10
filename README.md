# Very Simple Shelly CLI

A super simple interactive CLI, written in Python, to monitor and control Shelly Generation 2 and Generation 3 smart plugs (`switch:0`) and CCT bulbs (`cct:0`). 

---

## 🛠️ Features

- **Global Macros:** Includes global commands like `all on` and `all off` to control multiple nodes simultaneously.
- **Decoupled Architecture:** IP addresses are stored cleanly in an external `config.json` file.
- **Dynamic Identification:** Dynamically fetches user-defined custom device names and firmware variants on startup.
- **Pure JSON Export:** The `status full` option outputs a completely valid, unpolluted JSON tree across all devices—perfect for log redirection or integration with other automation pipelines.

---

## 🚀 Getting Started

### 1. Prerequisites
The script uses standard Python 3.x. Ensure you have the `requests` library installed:
```bash
pip install requests
```

### 2. File Layout
Keep the script and configuration template in the same local directory context:
```text
your-project-directory/
├── shelly_cli.py
└── config.json
```

### 3. Setup Configuration
When you run the script for the first time, it will automatically detect if `config.json` is missing, generate a clean template, and exit:
```bash
python shelly_cli.py
```

Open the n`config.json` file and add your specific Shelly device IPs:
```json
{
  "PLUG_IP": "CHANGE_ME",
  "BULB_IP": "CHANGE_ME"
}
```

---

## 🎮 Command Guide

Launch the interface by initializing the runtime thread:
```bash
python shelly-cli.py
```

Once inside the interactive environment (`shelly-cli>`), use the following commands:

### Monitoring State
- **`status`**  
  Prints a simplified, human-readable terminal summary of current states (Power state, load metrics, brightness levels, color temperature properties).
- **`status full`**  
  Queries endpoints and dumps a unified, **pure JSON tree** containing complete runtime metrics, hardware metadata, device configurations, and firmware identification tags.

### Control Commands
- **`plug on` / `plug off`**  
  Switches the smart plug on or off.
- **`bulb on` / `bulb off`**  
  Switches the CCT light output on or off.
- **`bulb set <brightness> <temperature>`**  
  Implicitly turns the bulb on and tunes variables. 
  - *Brightness Range:* `1` to `100` (%)
  - *Temperature Range:* Typical CCT bulbs accept `2700` to `6500` (Kelvin)
  - *Example:* `bulb set 45 3000`

### Global Macros & Management
- **`all on` / `all off`**  
  Executes an optimization loop to simultaneously apply the target power state across both the plug and bulb.
- **`help`**  
  Displays the CLI menu.
- **`exit` / `quit`** (or `Ctrl+C`)  
  Terminates the program context gracefully.
