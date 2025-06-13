import discord, json, asyncio, colorama, os
from discord.ext import commands
from datetime import datetime

colorama.init()

def load_auto_messages():
    try:
        with open("am.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_auto_messages(data):
    with open("am.json", "w") as f:
        json.dump(data, f, indent=4)

category_messages = {}
active_tasks = {}
tasks_dict = {}
sent_channels = set()

class AutoMessageScheduler:
    def __init__(self, bot):
        self.bot = bot
        self.auto_messages = load_auto_messages()
        self.tasks = {}
        self.running = False
        self.lock = asyncio.Lock()
        self.bg_task = None

    async def start(self):
        if not self.running:
            self.running = True
            self.bg_task = asyncio.create_task(self.run())

    async def stop(self):
        self.running = False
        if self.bg_task:
            self.bg_task.cancel()
            self.bg_task = None

    async def run(self):
        while self.running:
            try:
                now = datetime.utcnow().timestamp()
                async with self.lock:
                    for channel_id_str, task_info in list(self.auto_messages.items()):
                        channel_id = int(channel_id_str)
                        interval = int(task_info['time']) * 60
                        last_sent = task_info.get('last_sent', 0)
                        if now - last_sent >= interval:
                            channel = self.bot.get_channel(channel_id)
                            if channel:
                                try:
                                    await channel.send(task_info['content'])
                                    self.auto_messages[channel_id_str]['last_sent'] = now
                                    save_auto_messages(self.auto_messages)
                                except Exception as e:
                                    print(f"\033[91m[!] Error sending message to {channel_id}: {e}")
                            else:
                                print(f"\033[91m[!] Channel {channel_id} not found.")
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"\033[91m[!] Scheduler error: {e}")
                await asyncio.sleep(30)

    async def add(self, channel_id, time_in_min, content):
        async with self.lock:
            self.auto_messages[str(channel_id)] = {
                "time": time_in_min,
                "content": content,
                "last_sent": 0
            }
            save_auto_messages(self.auto_messages)

    async def remove(self, channel_id):
        async with self.lock:
            if str(channel_id) in self.auto_messages:
                del self.auto_messages[str(channel_id)]
                save_auto_messages(self.auto_messages)

    def list(self):
        return self.auto_messages

def load_json(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def load_config(config_file_path):
    with open(config_file_path, 'r') as config_file:
        config = json.load(config_file)
    return config

if __name__ == "__main__":
    config_file_path = "config.json"
    config = load_config(config_file_path)

prefix = config.get('prefix')
token = config.get('token')

Igz = commands.Bot(description='Made by 1gz',
                           command_prefix=prefix,
                           self_bot=True)

Igz.remove_command('help')

auto_message_scheduler = AutoMessageScheduler(Igz)

@Igz.event
async def on_ready():
    # Clear the console on ready
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"\033[92m[+] Logged in as: {Igz.user.name} (ID: {Igz.user.id})")
    await auto_message_scheduler.start()
    print("\033[92m[+] Auto-message scheduler started.")

@Igz.event
async def on_message(message):
    if message.author.bot:
        return
    await Igz.process_commands(message)
    
@Igz.command()
async def amlist(ctx):
    try:
        await ctx.message.delete()
    except discord.HTTPException:
        pass
    try:
        data = auto_message_scheduler.list()
        if not data:
            await ctx.send("## Auto Messages List:\n- **None**")
            print("\033[92m[+] AMLIST COMMAND USED")
            return

        formatted_message = "## Auto Messages List:\n"
        for channel_id, task_info in data.items():
            formatted_message += (
                f"- **Channel ID**: `{channel_id}`\n"
                f"  - **Interval**: `{task_info['time']} minutes`\n"
                f"  - **Content**: `{task_info['content']}`\n\n"
            )
        await ctx.send(formatted_message)
        print("\033[92m[+] AMLIST COMMAND USED")
    except Exception as e:
        await ctx.send(f"Failed to list Auto Messages: {e}")

@amlist.error
async def amlist_error(ctx, error):
    await ctx.send("Usage: `{0}amlist`".format(prefix))

@Igz.command()
async def startam(ctx, channel_id: int, time_in_min: int, *, content: str):
    try:
        await ctx.message.delete()
    except discord.HTTPException:
        pass
    try:
        data = auto_message_scheduler.list()
        if str(channel_id) in data:
            await ctx.send(f"[ ! ] Auto Message already running in <#{channel_id}>.")
            return
        await auto_message_scheduler.add(channel_id, time_in_min, content)
        await ctx.send(f"[ + ] Auto message set every {time_in_min} min(s) in <#{channel_id}>.")
        print(f"\033[92m[+] STARTAM COMMAND USED")
    except Exception as e:
        await ctx.send(f"[ ! ] Failed to start auto message: {e}")

@startam.error
async def startam_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Usage: `{prefix}startam <channel_id> <time_in_min> <content>`\nExample: `{prefix}startam 123456789012345678 10 Hello world!`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"[ ! ] Invalid argument type.\nUsage: `{prefix}startam <channel_id> <time_in_min> <content>`\nExample: `{prefix}startam 123456789012345678 10 Hello world!`")
    else:
        await ctx.send(f"[ ! ] Error: {error}")

@Igz.command()
async def stopam(ctx, channel_id: int):
    try:
        await ctx.message.delete()
    except discord.HTTPException:
        pass
    try:
        await auto_message_scheduler.remove(channel_id)
        await ctx.send(f"[ + ] Auto Message Stopped for <#{channel_id}>.")
        print(f"\033[92m[+] STOPAM COMMAND USED")
    except Exception as e:
        await ctx.send(f"[ ! ] Failed to stop auto message: {e}")
        print(f"\033[91m[!] STOPAM ERROR: {e}")

@stopam.error
async def stopam_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Usage: `{prefix}stopam <channel_id>`\nExample: `{prefix}stopam 123456789012345678`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"[ ! ] Invalid argument type.\nUsage: `{prefix}stopam <channel_id>`\nExample: `{prefix}stopam 123456789012345678`")
    else:
        await ctx.send(f"[ ! ] Error: {error}")

@Igz.event
async def on_guild_channel_create(channel):
    if isinstance(channel, discord.TextChannel):
        category_id = channel.category_id
        if category_id in active_tasks and active_tasks[category_id]:
            await asyncio.sleep(1)
            await channel.send(category_messages[category_id])

Igz.run(token)