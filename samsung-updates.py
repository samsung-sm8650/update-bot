#!/usr/bin/python3 -u
from copy import deepcopy
import json
import requests
import time
import urllib.request
import xml.etree.ElementTree as ET

with open("token.txt", "r") as file:
    token = file.read().rstrip("\n")

# Models to check
models = {
    # Galaxy S24
    "SM-S9210": ["BRI", "CHC"],
    "SC-51E": ["DCM"],
    "SCG25": ["KDI"],
    "SM-S921Q": ["SJP"],
    "SM-S921U": ["ATT"],
    "SM-S921U1": ["ATT"],
    "SM-S921W": ["BMC"],
    # Galaxy S24+
    "SM-S9260": ["BRI", "CHC"],
    "SM-S926U": ["ATT"],
    "SM-S926U1": ["ATT"],
    "SM-S926W": ["BMC"],
    # Galaxy S24 Ultra
    "SM-S9280": ["BRI", "CHC"],
    "SM-S928B": ["EUX"],
    "SC-52E": ["DCM"],
    "SCG26": ["KDI"],
    "SM-S928N": ["KOO"],
    "SM-S928Q": ["SJP"],
    "SM-S928U": ["ATT"],
    "SM-S928U1": ["ATT"],
    "SM-S928W": ["BMC"],
    # Galaxy Z Flip6
    "SM-F7410": ["BRI", "CHC"],
    "SM-F741B": ["EUX"],
    "SC-54E": ["DCM"],
    "SCG29": ["KDI"],
    "SM-F741N": ["KOO"],
    "SM-F741Q": ["SJP"],
    "SM-F741U": ["ATT"],
    "SM-F741U1": ["ATT"],
    "SM-F741W": ["BMC"],
    # Galaxy Z Fold6
    "SM-F9560": ["BRI", "CHC"],
    "SM-F956B": ["EUX"],
    "SC-55E": ["DCM"],
    "SCG28": ["KDI"],
    "SM-F956N": ["KOO"],
    "SM-F956Q": ["SJP"],
    "SM-F956U": ["ATT"],
    "SM-F956U1": ["ATT"],
    "SM-F956W": ["BMC"],
}

# JSON file with known updates
try:
    with open("samsung-versions.json") as jsonfile:
        try:
            updates = json.load(jsonfile)
        except:
            error("Unable to read samsung-versions.json")
except:
    updates = {}
    warning("File samsung-version.json not found")

def info(text): print(f"\033[94mINFO: \033[00m{text}")
def warning(text): print(f"\033[93mWARNING: \033[00m{text}")
def error(text): print(f"\033[91mERROR: \033[00m{text}")

def sendmessage(text):
    url = f"https://api.telegram.org/bot{token}/sendmessage"
    params = {"chat_id": "@samsung_sm8650_updates", "parse_mode": "HTML", "text": text}
    requests.post(url, params)

while True:
    diff_updates = deepcopy(updates)
    for model, csc_list in models.items():
        for csc in csc_list:
            url = "https://fota-cloud-dn.ospserver.net/firmware/" + csc + "/" + model +  "/version.xml"
            try:
                response = urllib.request.urlopen(url).read()
            except:
                warning(f"Unable to connect to {url}")
                time.sleep(60)
                break
            tree = ET.fromstring(response)

            for version in tree.iter("latest"):
                if version.text == None:
                    warning(f"No updates found for {model} ({csc})")
                    break
                if updates.get(model, None) == None:
                    updates[model] = {}
                fwver = version.text.split("/")
                osver = version.attrib["o"]

                info(f"{fwver[0]}: Got version from API")

                try:
                    if updates[model][csc] != None:
                        for key, val in updates[model].items():
                            if key == csc:
                                if val == [fwver[0], fwver[1], osver]:
                                    info(f"{fwver[0]}: Already discovered. Skipping")
                                    time.sleep(5)
                                else:
                                    break
                        else:
                            break
                except KeyError:
                    pass

                print(f"New update found!\nModel: {model}\nAP: {fwver[0]}\nCSC: {fwver[1]} ({csc})\nAndroid version: {osver}\n")
                sendmessage(f"<b>New update found!\nModel:</b> <code>{model}</code>\n<b>AP:</b> <code>{fwver[0]}</code>\n<b>CSC:</b> <code>{fwver[1]}</code> (<code>{csc}</code>)\n<b>Android version:</b> <code>{osver}</code>")
                updates[model].update({csc: [fwver[0], fwver[1], osver]})

                if diff_updates != updates:
                    info("Updating samsung-versions.json")
                    with open("samsung-versions.json", "w") as jsonfile:
                        json.dump(updates, jsonfile, ensure_ascii=False, indent=4)

                # Let's not overwhelm the APIs
                time.sleep(5)

    info("API scraping finished. Trying again in 20 minutes")
    time.sleep(1200)
