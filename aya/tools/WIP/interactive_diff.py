import argparse
from pathlib import Path

import aya
from aya import KismetDevice


# --- Style and Color constants ---
class Style:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"


def parse_kismet_log(file_path):
    """
    Parses a Kismet JSONL file and returns structured data about the devices.
    """
    aps: dict[str, aya.KismetDevice] = {}
    stas: dict[str, aya.KismetDevice] = {}
    probes = []
    if type(file_path) == str:
        file_path = Path(file_path)

    for device in aya.get_access_points(file_path):
        aps[device.mac] = device
    for device in aya.get_stas(file_path):
        stas[device.mac] = device
    probes: list[str] = set(
        sorted([probe for device in stas.values() for probe in device.probedSSIDs])
    )
    return aps, stas, probes


def parse_args():
    parser = argparse.ArgumentParser(
        description="Interactively compare two Kismet logs, with prompts for file conversion.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("baseline_file", help="Path to the baseline .kismet log file.")
    parser.add_argument(
        "comparison_file", help="Path to the comparison .kismet log file."
    )
    return parser.parse_args()


def report_new_and_missing(
    baseline_aps: list[KismetDevice],
    comp_aps: list[KismetDevice],
    baseline_clients: list[KismetDevice],
    comp_clients: list[KismetDevice],
):
    new_aps = set(comp_aps.keys()) - set(baseline_aps.keys())
    missing_aps = set(baseline_aps.keys()) - set(comp_aps.keys())
    new_clients = set(comp_clients.keys()) - set(baseline_clients.keys())
    missing_clients = set(baseline_clients.keys()) - set(comp_clients.keys())

    print("\n--- ðŸ›°ï¸ New and Missing Access Points ---")
    print(f"[+] New APs: {len(new_aps)}")
    for mac in sorted(new_aps):
        print(f"  - {mac} (SSID: {comp_aps[mac].name})")
    print(f"[-] Missing APs: {len(missing_aps)}")
    for mac in sorted(missing_aps):
        print(f"  - {mac} (SSID: {baseline_aps[mac].name})")

    print("\n--- ðŸ’» New and Missing Clients ---")
    print(f"[+] New Clients: {len(new_clients)}")
    for mac in sorted(new_clients):
        print(f"  - {mac}")
    print(f"[-] Missing Clients: {len(missing_clients)}")
    for mac in sorted(missing_clients):
        print(f"  - {mac}")


def report_environmental_changes(
    baseline_aps, comp_aps, baseline_clients, comp_clients
):
    print("\n" + "=" * 50 + "\n")
    print("--- ðŸ”„ Environmental Changes for Common Devices ---")
    _report_ap_changes(baseline_aps, comp_aps)
    _report_client_changes(baseline_clients, comp_clients)


def _report_ap_changes(baseline_aps, comp_aps):
    common_aps = baseline_aps.keys() & comp_aps.keys()
    print(f"\n[*] Analyzing {len(common_aps)} common Access Points for changes...")
    for mac in sorted(common_aps):
        base_ap = baseline_aps[mac]
        comp_ap = comp_aps[mac]
        changes = _get_ap_changes(base_ap, comp_ap)
        if changes:
            print(f"  - AP: {mac} (SSID: {base_ap.name})")
            for change in changes:
                print(f"    - {change}")


def _get_ap_changes(base_ap: KismetDevice, comp_ap: KismetDevice):
    changes = []
    if base_ap.name != comp_ap.name:
        changes.append(f"SSID changed: '{base_ap.name}' -> '{comp_ap.name}'")
    if base_ap.channel != comp_ap.channel:
        changes.append(f"Channel changed: {base_ap.channel} -> {comp_ap.channel}")
    if base_ap.crypt != comp_ap.crypt:
        changes.append(f"Encryption changed: {base_ap.crypt} -> {comp_ap.crypt}")
    return changes


def _report_client_changes(baseline_clients, comp_clients):
    common_clients = baseline_clients.keys() & comp_clients.keys()
    print(f"\n[*] Analyzing {len(common_clients)} common Clients for changes...")
    for mac in sorted(common_clients):
        base_client, comp_client = baseline_clients[mac], comp_clients[mac]
        added_probes, removed_probes = _get_client_probe_changes(
            base_client, comp_client
        )
        if added_probes or removed_probes:
            print(f"  - Client: {mac}")
            if added_probes:
                print(f"    - Started probing for: {', '.join(sorted(added_probes))}")
            if removed_probes:
                print(f"    - Stopped probing for: {', '.join(sorted(removed_probes))}")


def _get_client_probe_changes(base_client, comp_client):
    added_probes = comp_client["probed_ssids"] - base_client["probed_ssids"]
    removed_probes = base_client["probed_ssids"] - comp_client["probed_ssids"]
    return added_probes, removed_probes


def report_probed_ssid_analysis(baseline_probes, comp_probes):
    print("\n" + "=" * 50 + "\n")
    print("--- ðŸ“¡ Probed SSID Analysis ---")
    newly_probed_ssids = comp_probes - baseline_probes
    no_longer_probed_ssids = baseline_probes - comp_probes

    print(f"\n[+] New SSIDs being probed for: {len(newly_probed_ssids)}")
    for ssid in sorted(newly_probed_ssids):
        print(f"  - '{ssid}'")
    print(f"\n[-] SSIDs no longer being probed for: {len(no_longer_probed_ssids)}")
    for ssid in sorted(no_longer_probed_ssids):
        print(f"  - '{ssid}'")


def main():
    args = parse_args()

    print("\n--- ðŸ” Processing Kismet Logs ---")
    baseline_aps, baseline_clients, baseline_probes = parse_kismet_log(
        args.baseline_file
    )
    comp_aps, comp_clients, comp_probes = parse_kismet_log(args.comparison_file)

    report_new_and_missing(baseline_aps, comp_aps, baseline_clients, comp_clients)
    report_environmental_changes(baseline_aps, comp_aps, baseline_clients, comp_clients)
    report_probed_ssid_analysis(baseline_probes, comp_probes)


if __name__ == "__main__":
    main()
