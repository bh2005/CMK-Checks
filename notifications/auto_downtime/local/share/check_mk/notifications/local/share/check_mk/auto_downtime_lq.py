#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Downtime mit Livestatus - EMPFOHLEN für Checkmk 2.4
Schnell, zuverlässig, keine Dependencies
"""

import sys
import os
import time
from datetime import datetime, timedelta

# Add OMD libs
omd_root = os.getenv("OMD_ROOT", "")
if omd_root:
    sys.path.insert(0, os.path.join(omd_root, "lib", "python3"))

try:
    import livestatus
    HAS_LIVESTATUS = True
except ImportError:
    HAS_LIVESTATUS = False
    import socket

from cmk.notification_plugins.utils import collect_context


def send_livestatus_command(command):
    """Send command via Livestatus."""
    try:
        if HAS_LIVESTATUS:
            conn = livestatus.SingleSiteConnection(f"unix:{omd_root}/tmp/run/live")
            conn.command(command)
            return True
        else:
            # Fallback to socket
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(f"{omd_root}/tmp/run/live")
            sock.send(f"COMMAND [{int(time.time())}] {command}\n".encode())
            sock.close()
            return True
    except Exception as e:
        sys.stderr.write(f"Livestatus command failed: {e}\n")
        return False


def get_host_downtimes(hostname):
    """Get all downtimes for a host."""
    try:
        if HAS_LIVESTATUS:
            conn = livestatus.SingleSiteConnection(f"unix:{omd_root}/tmp/run/live")
            query = f"GET downtimes\nColumns: id comment\nFilter: host_name = {hostname}\n"
            result = conn.query_table(query)
            return result
        else:
            # Socket fallback
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(f"{omd_root}/tmp/run/live")
            query = f"GET downtimes\nColumns: id comment\nFilter: host_name = {hostname}\n"
            sock.send(query.encode())
            sock.shutdown(socket.SHUT_WR)
            response = sock.recv(100000000).decode()
            sock.close()
            
            lines = response.strip().split('\n')
            return [line.split(';') for line in lines if line]
    except Exception as e:
        sys.stderr.write(f"Failed to query downtimes: {e}\n")
        return []


def set_flexible_downtime(hostname, comment):
    """
    Set flexible downtime without end time.
    Duration 0 means: until manually removed or host UP.
    """
    start_time = int(time.time())
    # Sehr weit in der Zukunft (10 Jahre) = faktisch "kein Ende"
    end_time = start_time + (10 * 365 * 24 * 3600)
    
    # SCHEDULE_HOST_SVC_DOWNTIME = Host + alle Services
    command = (
        f"SCHEDULE_HOST_SVC_DOWNTIME;{hostname};{start_time};{end_time};"
        f"1;0;0;auto_downtime;{comment}"
    )
    
    return send_livestatus_command(command)


def delete_downtime(downtime_id):
    """Delete a specific downtime by ID."""
    command = f"DEL_HOST_DOWNTIME;{downtime_id}"
    return send_livestatus_command(command)


def main():
    raw_context = collect_context()
    
    what = raw_context.get("WHAT")
    state = raw_context.get("HOSTSTATE")
    hostname = raw_context.get("HOSTNAME")
    
    if what != "HOST":
        sys.stdout.write("Only HOST events processed\n")
        return 0
    
    # Get threshold from rule
    try:
        duration_days = float(raw_context.get("PARAMETER_DURATION_DAYS", "2.0"))
    except ValueError:
        duration_days = 2.0
    
    threshold = timedelta(days=duration_days)
    
    # ========================================
    # CASE 1: HOST DOWN
    # ========================================
    if state == "DOWN":
        last_up_unix = raw_context.get("HOSTLASTUPTIME")
        
        if not last_up_unix or not last_up_unix.isdigit():
            sys.stdout.write(f"No valid HOSTLASTUPTIME for {hostname}\n")
            return 0
        
        last_up = datetime.fromtimestamp(int(last_up_unix))
        now = datetime.now()
        duration = now - last_up
        
        if duration < threshold:
            sys.stdout.write(
                f"{hostname} DOWN for {duration.days}d {duration.seconds//3600}h "
                f"< {duration_days}d threshold -> skip\n"
            )
            return 0
        
        # Set flexible downtime
        comment = f"Auto-Downtime: Host DOWN seit > {duration_days} Tagen"
        
        if set_flexible_downtime(hostname, comment):
            sys.stdout.write(f"✓ Flexible downtime set for {hostname}\n")
            return 0
        else:
            sys.stderr.write(f"✗ Failed to set downtime for {hostname}\n")
            return 2
    
    # ========================================
    # CASE 2: HOST UP (RECOVERY)
    # ========================================
    elif state == "UP":
        downtimes = get_host_downtimes(hostname)
        deleted = 0
        
        for dt_row in downtimes:
            if len(dt_row) < 2:
                continue
            
            dt_id = dt_row[0]
            comment = dt_row[1] if len(dt_row) > 1 else ""
            
            # Only delete OUR downtimes
            if "Auto-Downtime: Host DOWN seit" in comment:
                if delete_downtime(dt_id):
                    deleted += 1
        
        if deleted > 0:
            sys.stdout.write(f"✓ Removed {deleted} auto-downtime(s) for {hostname}\n")
        else:
            sys.stdout.write(f"No auto-downtimes found for {hostname}\n")
        
        return 0
    
    else:
        sys.stdout.write(f"Unknown HOSTSTATE: {state}\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())