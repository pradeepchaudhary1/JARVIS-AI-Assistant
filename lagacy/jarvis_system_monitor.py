"""
JARVIS System Monitor — Issue #5 Fix
Battery, RAM, CPU, Storage, Network status
"""
import os, json, platform
from datetime import datetime
from livekit.agents import function_tool

try:
    import psutil
    PSUTIL = True
except ImportError:
    PSUTIL = False


def _no_psutil():
    return "psutil nahi mila. Run karo: pip install psutil"


@function_tool
async def get_battery_status() -> str:
    """Battery percentage aur charging status batao"""
    if not PSUTIL: return _no_psutil()
    try:
        b = psutil.sensors_battery()
        if b is None:
            return "Battery sensor nahi mila (Desktop PC ho sakta hai)."
        status = "Charging ✅" if b.power_plugged else "Battery pe 🔋"
        mins   = int(b.secsleft / 60) if b.secsleft > 0 else -1
        time_left = f"{mins} minutes bachi" if mins > 0 else "Calculating..."
        return (
            f"🔋 Battery: {b.percent:.0f}%\n"
            f"⚡ Status: {status}\n"
            f"⏱ Time left: {time_left}"
        )
    except Exception as e:
        return f"Battery error: {e}"


@function_tool
async def get_ram_usage() -> str:
    """RAM usage batao"""
    if not PSUTIL: return _no_psutil()
    try:
        r = psutil.virtual_memory()
        return (
            f"💾 RAM Usage:\n"
            f"  Total:     {r.total/1e9:.1f} GB\n"
            f"  Used:      {r.used/1e9:.1f} GB ({r.percent}%)\n"
            f"  Available: {r.available/1e9:.1f} GB\n"
            f"  Status:    {'⚠ High' if r.percent > 80 else '✅ Normal'}"
        )
    except Exception as e:
        return f"RAM error: {e}"


@function_tool
async def get_cpu_usage() -> str:
    """CPU usage batao"""
    if not PSUTIL: return _no_psutil()
    try:
        import asyncio
        cpu = await asyncio.get_event_loop().run_in_executor(
            None, lambda: psutil.cpu_percent(interval=1)
        )
        freq  = psutil.cpu_freq()
        cores = psutil.cpu_count()
        return (
            f"🖥 CPU Usage:\n"
            f"  Usage:  {cpu}%\n"
            f"  Cores:  {cores}\n"
            f"  Speed:  {freq.current:.0f} MHz\n"
            f"  Status: {'⚠ High load' if cpu > 80 else '✅ Normal'}"
        )
    except Exception as e:
        return f"CPU error: {e}"


@function_tool
async def get_storage_usage() -> str:
    """Storage/Disk usage batao"""
    if not PSUTIL: return _no_psutil()
    try:
        result = "💿 Storage Usage:\n"
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                result += (
                    f"\n  Drive {part.mountpoint}:\n"
                    f"    Total: {usage.total/1e9:.1f} GB\n"
                    f"    Used:  {usage.used/1e9:.1f} GB ({usage.percent}%)\n"
                    f"    Free:  {usage.free/1e9:.1f} GB\n"
                    f"    Status: {'⚠ Almost full' if usage.percent > 85 else '✅ OK'}"
                )
            except Exception:
                pass
        return result
    except Exception as e:
        return f"Storage error: {e}"


@function_tool
async def get_system_health() -> str:
    """Complete system health report — CPU, RAM, Battery, Storage"""
    if not PSUTIL: return _no_psutil()
    try:
        import asyncio
        # CPU
        cpu = await asyncio.get_event_loop().run_in_executor(
            None, lambda: psutil.cpu_percent(interval=1)
        )
        ram   = psutil.virtual_memory()
        disk  = psutil.disk_usage('C:\\')
        bat   = psutil.sensors_battery()
        bat_str = f"{bat.percent:.0f}% ({'Charging' if bat.power_plugged else 'Battery'})" if bat else "N/A"

        health = "🟢 Good" if cpu < 70 and ram.percent < 80 else "🟡 Warning" if cpu < 90 else "🔴 Critical"

        return (
            f"📊 SYSTEM HEALTH REPORT\n"
            f"{'='*30}\n"
            f"🖥 CPU:     {cpu}%\n"
            f"💾 RAM:     {ram.percent}% ({ram.used/1e9:.1f}/{ram.total/1e9:.1f} GB)\n"
            f"💿 Disk C:  {disk.percent}% ({disk.used/1e9:.0f}/{disk.total/1e9:.0f} GB)\n"
            f"🔋 Battery: {bat_str}\n"
            f"🏥 Health:  {health}\n"
            f"⏰ Time:    {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        )
    except Exception as e:
        return f"System health error: {e}"


@function_tool
async def get_running_processes() -> str:
    """Top 5 CPU-consuming processes batao"""
    if not PSUTIL: return _no_psutil()
    try:
        procs = []
        for p in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
            try:
                procs.append(p.info)
            except Exception:
                pass
        procs.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        result = "🔄 Top Processes:\n"
        for p in procs[:5]:
            result += f"  {p['name']}: CPU {p.get('cpu_percent',0):.1f}% | RAM {p.get('memory_percent',0):.1f}%\n"
        return result
    except Exception as e:
        return f"Process error: {e}"
