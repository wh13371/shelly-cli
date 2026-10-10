import os
import sys
import json
import requests

CONFIG_FILE = "config.json"
PLUG_IP = ""
BULB_IP = ""

DEVICE_NAMES = {
    "plug": "Smart Plug",
    "bulb": "CCT Bulb"
}

def load_network_config():
    global PLUG_IP, BULB_IP
    if not os.path.exists(CONFIG_FILE):
        default_config = {"PLUG_IP": "192.168.1.50", "BULB_IP": "192.168.1.51"}
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(default_config, f, indent=2)
            print(f"[{CONFIG_FILE}] Generated standard template file.")
            print("Please fill in your actual device IPs and restart.")
            sys.exit(0)
        except Exception as e:
            print(f"Critical write error: {e}")
            sys.exit(1)
    try:
        with open(CONFIG_FILE, "r") as f:
            config_data = json.load(f)
            PLUG_IP = config_data.get("PLUG_IP", "").strip()
            BULB_IP = config_data.get("BULB_IP", "").strip()
            if not PLUG_IP or not BULB_IP:
                print("Error: Missing parameters in config.json")
                sys.exit(1)
    except Exception as e:
        print(f"Critical read error: {e}")
        sys.exit(1)

def fetch_device_name(ip_address, default_label):
    try:
        res = requests.get(f"http://{ip_address}/rpc/Sys.GetConfig", timeout=2).json()
        custom_name = res.get("device", {}).get("name")
        if custom_name:
            return custom_name
    except Exception:
        pass
    return default_label

def initialize_names():
    print("Connecting to devices and fetching names...")
    DEVICE_NAMES["plug"] = fetch_device_name(PLUG_IP, "Smart Plug")
    DEVICE_NAMES["bulb"] = fetch_device_name(BULB_IP, "CCT Bulb")
    print(f"-> Detected Plug Name: '{DEVICE_NAMES['plug']}'")
    print(f"-> Detected Bulb Name: '{DEVICE_NAMES['bulb']}'\n")

def get_raw_status(ip_address):
    try:
        return requests.get(f"http://{ip_address}/rpc/Shelly.GetStatus", timeout=3).json()
    except Exception as e:
        return {"error": f"Failed connection: {e}"}

def extract_firmware(data, ip_address):
    if "error" in data:
        return "Unknown"
    fw = data.get("ver") or data.get("fw_id")
    if fw:
        return fw
    sys_block = data.get("sys", {})
    fw = sys_block.get("fw_id") or sys_block.get("ver")
    if fw:
        return fw
    try:
        info_data = requests.get(f"http://{ip_address}/rpc/Shelly.GetDeviceInfo", timeout=2).json()
        return info_data.get("ver") or info_data.get("fw_id") or "Unknown"
    except Exception:
        return "Unknown"

def query_plug():
    res = get_raw_status(PLUG_IP)
    name = DEVICE_NAMES["plug"]
    if "error" in res:
        print(f"[{name}] {res['error']}")
        return
    switch = res.get("switch:0", {})
    state = "ON" if switch.get("output") else "OFF"
    power = switch.get("apower", 0)
    print(f"[{name}] Status: {state} | Power Draw: {power}W")

def query_bulb():
    res = get_raw_status(BULB_IP)
    name = DEVICE_NAMES["bulb"]
    if "error" in res:
        print(f"[{name}] {res['error']}")
        return
    cct = res.get("cct:0", {})
    if cct:
        state = "ON" if cct.get("output") else "OFF"
        brightness = cct.get("brightness", 0)
        ct = cct.get("ct") or cct.get("temperature") or cct.get("temp") or "Unknown"
        print(f"[{name}] Status: {state} | Brightness: {brightness}% | Color Temp: {ct}K")
    else:
        print(f"[{name}] Error: 'cct:0' block not found.")

def control_plug(turn_on=True, silent=False):
    name = DEVICE_NAMES["plug"]
    state_str = "true" if turn_on else "false"
    try:
        requests.get(f"http://{PLUG_IP}/rpc/Switch.Set?id=0&on={state_str}", timeout=3)
        if not silent:
            print(f"[{name}] Successfully turned {'ON' if turn_on else 'OFF'}")
    except Exception as e:
        print(f"[{name}] Error: {e}")

def control_bulb(turn_on=True, brightness=None, temp=None, silent=False):
    name = DEVICE_NAMES["bulb"]
    url = f"http://{BULB_IP}/rpc/CCT.Set?id=0"
    if turn_on is not None:
        url += f"&on={'true' if turn_on else 'false'}"
    if brightness is not None:
        url += f"&brightness={brightness}"
    if temp is not None:
        url += f"&temp={temp}"
    try:
        requests.get(url, timeout=3)
        if not silent:
            action_msgs = []
            if turn_on is not None: action_msgs.append(f"Power={'ON' if turn_on else 'OFF'}")
            if brightness is not None: action_msgs.append(f"Brightness={brightness}%")
            if temp is not None: action_msgs.append(f"Temp={temp}K")
            print(f"[{name}] Updated settings: {', '.join(action_msgs)}")
    except Exception as e:
        print(f"[{name}] Error: {e}")

def print_help():
    print("Available Commands:")
    print("  status                   - View basic status summaries")
    print("  status full              - Print entire merged raw JSON trees")
    print("  plug on / off            - Switch the smart plug switch channel")
    print("  bulb on / off            - Switch the light channel output")
    print("  bulb set <pct> <kelvin>  - Adjust brightness (1-100) and color temperature")
    print("  all on / off             - Global macro toggle command loop")
    print("  help                     - Show this interaction helper menu")
    print("  exit / quit              - Terminate application thread context")

def main():
    print("====================================")
    print("    Very Simple Shelly CLI    ")
    print("====================================")
    load_network_config()
    initialize_names()
    print_help()
    while True:
        try:
            user_input = input("\nshelly-cli> ").strip().lower()
            if not user_input:
                continue
            args = user_input.split()
            cmd = args[0]
            if cmd in ["exit", "quit"]:
                print("Goodbye!")
                sys.exit(0)
            elif cmd == "help":
                print_help()
            elif cmd == "status":
                if len(args) > 1 and args[1] == "full":
                    p_data = get_raw_status(PLUG_IP)
                    b_data = get_raw_status(BULB_IP)
                    p_fw = extract_firmware(p_data, PLUG_IP)
                    b_fw = extract_firmware(b_data, BULB_IP)
                    if "error" not in p_data:
                        p_data["device_name"] = DEVICE_NAMES["plug"]
                        p_data["firmware_version"] = p_fw
                    if "error" not in b_data:
                        b_data["device_name"] = DEVICE_NAMES["bulb"]
                        b_data["firmware_version"] = b_fw
                    print(json.dumps({"plug": p_data, "bulb": b_data}, indent=2))
                else:
                    print("\n--- Current Home Status ---")
                    query_plug()
                    query_bulb()
            elif cmd == "plug":
                if len(args) < 2 or args[1] not in ["on", "off"]:
                    print("Usage: plug on | plug off")
                    continue
                control_plug(turn_on=(args[1] == "on"))
            elif cmd == "bulb":
                if len(args) < 2:
                    print("Usage: bulb on | bulb off | bulb set <brightness> <temp>")
                    continue
                sub = args[1]
                if sub in ["on", "off"]:
                    control_bulb(turn_on=(sub == "on"))
                elif sub == "set":
                    if len(args) < 4:
                        print("Usage: bulb set <brightness> <temp>")
                        continue
                    try:
                        control_bulb(turn_on=True, brightness=int(args[2]), temp=int(args[3]))
                    except ValueError:
                        print("Error: Input arguments must be whole numeric integers.")
            elif cmd == "all":
                if len(args) < 2 or args[1] not in ["on", "off"]:
                    print("Usage: all on | all off")
                    continue
                state = (args[1] == "on")
                print(f"\nExecuting macro: Turning everything {'ON' if state else 'OFF'}...")
                control_plug(turn_on=state, silent=True)
                control_bulb(turn_on=state, silent=True)
                print("Macro completed successfully.")
            else:
                print(f"Unknown command: '{cmd}'. Type 'help' for instructions.")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            sys.exit(0)

if __name__ == "__main__":
    main()
