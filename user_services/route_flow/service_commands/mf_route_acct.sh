#!/bin/bash
# Per-route byte counters for node_exporter's textfile collector.
# Installed on each experiment node by install_route_acct.yml and run by mf-route-acct.service.
#
#   usage: mf_route_acct.sh NODE_NAME PEERS_FILE [TEXTFILE_DIR]
#
# PEERS_FILE has one "<peer_name> <peer_ip>" per line (a peer may have several IPs).
# For each peer IP, two count-only iptables rules (no target) are kept in OUTPUT/INPUT,
# tagged with the comment "mfacct". Every 5 s their byte counters are summed per peer and
# written atomically to TEXTFILE_DIR/mf_route.prom as
#   mf_route_bytes_total{mf_node="<NODE_NAME>",mf_peer="<peer>",direction="tx|rx"} <bytes>

node="$1"
peers_file="$2"
textfile_dir="${3:-/var/lib/node_exporter}"
out="$textfile_dir/mf_route.prom"

if [ -z "$node" ] || [ ! -r "$peers_file" ]; then
    echo "usage: $0 NODE_NAME PEERS_FILE [TEXTFILE_DIR]" >&2
    exit 1
fi
mkdir -p "$textfile_dir"

while true; do
    declare -A tx=() rx=()
    out_rules=$(iptables -nvxL OUTPUT 2>/dev/null | grep mfacct)
    in_rules=$(iptables -nvxL INPUT 2>/dev/null | grep mfacct)
    while read -r peer ip _; do
        [ -z "$ip" ] && continue
        case "$peer" in \#*) continue ;; esac
        # (re)create the counting rules if missing, e.g. after a firewall reload
        iptables -C OUTPUT -d "$ip" -m comment --comment mfacct 2>/dev/null || iptables -I OUTPUT -d "$ip" -m comment --comment mfacct
        iptables -C INPUT -s "$ip" -m comment --comment mfacct 2>/dev/null || iptables -I INPUT -s "$ip" -m comment --comment mfacct
        t=$(echo "$out_rules" | grep -F " $ip " | awk '{s+=$2} END {print s+0}')
        r=$(echo "$in_rules" | grep -F " $ip " | awk '{s+=$2} END {print s+0}')
        tx[$peer]=$(( ${tx[$peer]:-0} + t ))
        rx[$peer]=$(( ${rx[$peer]:-0} + r ))
    done < "$peers_file"
    {
        echo "# HELP mf_route_bytes_total Bytes sent to (tx) / received from (rx) each experiment peer, from iptables counters."
        echo "# TYPE mf_route_bytes_total counter"
        for peer in "${!tx[@]}"; do
            echo "mf_route_bytes_total{mf_node=\"$node\",mf_peer=\"$peer\",direction=\"tx\"} ${tx[$peer]}"
            echo "mf_route_bytes_total{mf_node=\"$node\",mf_peer=\"$peer\",direction=\"rx\"} ${rx[$peer]}"
        done
    } > "$out.tmp" && chmod 644 "$out.tmp" && mv "$out.tmp" "$out"
    unset tx rx
    sleep 5
done
