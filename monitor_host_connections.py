#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import socket
from datetime import datetime
from prettytable import PrettyTable
from scapy.all import ARP, Ether, srp, sniff, IP, TCP, UDP, DNS


# =========================
# Scan LAN
# =========================
def scan_lan(network="192.168.1.0/24"):
    print("\n🔍 Scan du réseau local...\n")

    packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network)
    result = srp(packet, timeout=2, verbose=0)[0]

    devices = []

    for sent, received in result:
        ip = received.psrc
        mac = received.hwsrc

        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except:
            hostname = "N/A"

        devices.append({
            "ip": ip,
            "mac": mac,
            "hostname": hostname
        })

    return devices


# =========================
# Affichage tableau
# =========================
def display_devices(devices):
    table = PrettyTable()
    table.field_names = ["Index", "IP", "MAC", "Hostname"]

    for i, dev in enumerate(devices):
        table.add_row([i, dev["ip"], dev["mac"], dev["hostname"]])

    print(table)


# =========================
# Extraction protocole
# =========================
def extract_protocol(packet):

    proto = "UNKNOWN"
    host = ""

    if packet.haslayer(DNS):
        proto = "DNS"
        try:
            host = packet[DNS].qd.qname.decode()
        except:
            pass

    elif packet.haslayer(TCP):

        sport = packet[TCP].sport
        dport = packet[TCP].dport

        if dport == 80 or sport == 80:
            proto = "HTTP"

        elif dport == 443 or sport == 443:
            proto = "TLS/HTTPS"

    elif packet.haslayer(UDP):
        proto = "UDP"

    return proto, host


# =========================
# Sniff temps réel
# =========================
def sniff_traffic(target_ip, csv_file="audit_log.csv"):

    print(f"\n📡 Audit temps réel pour {target_ip}")
    print("CTRL+C pour arrêter\n")

    with open(csv_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Source", "Destination", "Protocol", "Host"])

        def process_packet(packet):

            if not packet.haslayer(IP):
                return

            src = packet[IP].src
            dst = packet[IP].dst

            if src != target_ip and dst != target_ip:
                return

            # Filtre multicast inutile
            if dst.startswith("224.") or dst.startswith("239."):
                return

            proto, host = extract_protocol(packet)

            timestamp = datetime.now().strftime("%H:%M:%S")

            print(f"{timestamp} | {src} → {dst} | {proto} | {host}")

            writer.writerow([timestamp, src, dst, proto, host])

        sniff(prn=process_packet, store=False)


# =========================
# MAIN
# =========================
def main():

    devices = scan_lan()

    if not devices:
        print("❌ Aucun device détecté")
        return

    display_devices(devices)

    index = int(input("\n👉 Choisir index machine à surveiller : "))
    target_ip = devices[index]["ip"]

    sniff_traffic(target_ip)


if __name__ == "__main__":
    main()
