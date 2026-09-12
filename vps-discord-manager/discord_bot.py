#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    print("DISCORD_BOT_TOKEN is missing. Set it in a .env file or environment variable.")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent
VPS_ADMIN = PROJECT_ROOT / "vps_admin.py"

intents = discord.Intents.default()
bot = discord.Client(intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")


def run_vps_admin(args):
    if not VPS_ADMIN.exists():
        return "vps_admin.py is missing from the project root."

    result = subprocess.run([sys.executable, str(VPS_ADMIN), *args], capture_output=True, text=True)
    output = (result.stdout or "").strip()
    error = (result.stderr or "").strip()
    return output or error or "No output."


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if not message.content.startswith("!vps"):
        return

    args = message.content.strip().split()
    if len(args) < 2:
        await message.channel.send(
            "Usage:\n"
            "!vps create <name> [cpu] [ram_mb] [disk_gb]\n"
            "!vps list\n"
            "!vps dashboard\n"
            "!vps host-info\n"
            "!vps status <name>\n"
            "!vps start <name>\n"
            "!vps stop <name>\n"
            "!vps restart <name>\n"
            "!vps destroy <name>\n"
            "!vps ssh <name>\n"
            "!vps ssh-key list\n"
            "!vps ssh-key generate <name>\n"
            "!vps ssh-key show <name>\n"
            "!vps snapshot create <name> [label]\n"
            "!vps snapshot list <name>\n"
            "!vps snapshot delete <name> <label>\n"
            "!vps cleanup [all|backups|snapshots|logs]\n"
            "!vps nightly-snapshot\n"
            "!vps inject-key <vm-name> [key-name]\n"
            "!vps logs <name>"
        )
        return

    command = args[1]

    if command in {"list", "dashboard", "host-info"}:
        output = run_vps_admin([command])
        await message.channel.send(f"```{output}```")
        return

    if command == "create":
        if len(args) < 3:
            await message.channel.send("Please provide a VM name. Example: !vps create demo-vps 2 4096 40")
            return
        output = run_vps_admin(["create", *args[2:]])
        await message.channel.send(f"```{output}```")
        return

    if command == "status":
        if len(args) < 3:
            await message.channel.send("Usage: !vps status <vm-name>")
            return
        output = run_vps_admin(["status", args[2]])
        await message.channel.send(f"```{output}```")
        return

    if command in {"start", "stop", "restart", "destroy"}:
        if len(args) < 3:
            await message.channel.send(f"Usage: !vps {command} <vm-name>")
            return
        output = run_vps_admin([command, args[2]])
        await message.channel.send(f"```{output}```")
        return

    if command == "ssh":
        if len(args) < 3:
            await message.channel.send("Usage: !vps ssh <vm-name>")
            return
        output = run_vps_admin(["ssh", args[2]])
        await message.channel.send(f"```{output}```")
        return

    if command == "ssh-key":
        if len(args) < 3:
            await message.channel.send("Usage: !vps ssh-key [list|generate|show|add|remove]")
            return
        subcommand = args[2]
        extra = args[3:]
        output = run_vps_admin(["ssh-key", subcommand, *extra])
        await message.channel.send(f"```{output}```")
        return

    if command == "snapshot":
        if len(args) < 3:
            await message.channel.send("Usage: !vps snapshot [create|list|delete|cleanup] ...")
            return
        output = run_vps_admin(["snapshot", *args[2:]])
        await message.channel.send(f"```{output}```")
        return

    if command == "cleanup":
        target = args[2] if len(args) > 2 else "all"
        output = run_vps_admin(["cleanup", target])
        await message.channel.send(f"```{output}```")
        return

    if command == "logs":
        if len(args) < 3:
            await message.channel.send("Usage: !vps logs <vm-name>")
            return
        output = run_vps_admin(["logs", args[2]])
        await message.channel.send(f"```{output}```")
        return

    if command == "nightly-snapshot":
        output = run_vps_admin(["nightly-snapshot"])
        await message.channel.send(f"```{output}```")
        return

    if command == "inject-key":
        if len(args) < 3:
            await message.channel.send("Usage: !vps inject-key <vm-name> [key-name]")
            return
        extra = [args[2]]
        if len(args) > 3:
            extra.append(args[3])
        output = run_vps_admin(["inject-key", *extra])
        await message.channel.send(f"```{output}```")
        return

    await message.channel.send("Unknown command. Run !vps help for the full command list.")


bot.run(TOKEN)
