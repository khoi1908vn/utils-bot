# the code must be updated to see this line :3
from discord import app_commands, Intents, Client, Interaction, Object, Embed, File, Game, Status, Color, Member
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from os import environ, system
from keep_alive import ka
from io import BytesIO
from jsondb import get_whitelist, update_whitelist, beta_check
# from enum import Enum

"""
-------------------------------------------------
DEFINING VARS
-------------------------------------------------
"""
class configurations:
    bot_token = environ.get('bot_token') 
    owner_ids = [806432782111735818]
    owner_guild_id = environ.get('owner_guild_id')
    beta = True
    max_global_ratelimit = 5
    default_maintenance_status = False

intents = Intents.default()
intents.members = True
intents.message_content = True
client = Client(intents=intents)
tree = app_commands.CommandTree(client)

def get_screenshot(url, window_height: int, window_width: int):
    options = Options()
    for arg in ['--no-sandbox', '--disable-dev-shm-usage', '--headless', '--disable-gpu', '--window-position=0,0', f'--window-size={window_height},{window_width}']: options.add_argument(arg)
    with webdriver.Chrome(options=options) as driver:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body[not(@class='loading')]")))
        image_bytes = driver.get_screenshot_as_png()
    return image_bytes

"""
-------------------------------------------------
BASE COMMANDS
-------------------------------------------------
"""  
@tree.command(name='eval', description='OWNER ONLY - execute python scripts via eval()', guild=Object(id=configurations.owner_guild_id))
async def scripteval(interaction: Interaction, script: str):
    await interaction.response.defer(ephemeral=True)
    if interaction.user.id not in configurations.owner_ids:
        await interaction.followup.send(embed=Embed(title="Unauthorized", description="You must be the owner to use this command!", color=Color.red()), ephemeral=True)
        return
    
    try:
        result = eval(script)
    except Exception as e:
        print("""----------Exception in command /eval----------""")
        print(e)
        print("""----------End----------""")
        await interaction.followup.send(embed=Embed(title="Exception occurred", description=str(e), color=Color.red()), ephemeral=True)
    else:
        if result is not None:
            await interaction.followup.send(embed=Embed(title="Result", description=str(result), color=Color.green()), ephemeral=True)
        else:
            await interaction.followup.send(embed=Embed(title="Script executed", color=Color.green()), ephemeral=True)

@tree.command(name='sync', description='OWNER ONLY - sync all commands to all guilds manually', guild=Object(id=configurations.owner_guild_id))
async def sync(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    if interaction.user.id not in configurations.owner_ids:
        await interaction.followup.send(embed=Embed(title="Unauthorized", description="You must be the owner to use this command!", color=Color.red()), ephemeral=True)
        return
    
    await client.change_presence(activity=Game('syncing...'), status=Status.dnd)
    tree.copy_global_to(guild=Object(id=configurations.owner_guild_id))
    await tree.sync()
    print(f'[+] Command tree synced via /sync by {interaction.user.id} ({interaction.user.display_name}')
    await interaction.followup.send(embed=Embed(title="Command tree synced", color=Color.green(), description='Successfully synced the global command tree to all guilds'), ephemeral=True)
    await client.change_presence(activity=Game('synced. reloading...'), status=Status.dnd)
    sleep(2)
    await client.change_presence(activity=Game('utils-bot'), status=Status.online)


@tree.command(name='restartbot', description='OWNER ONLY - Restart the bot', guild=Object(id=configurations.owner_guild_id))
async def restartbot(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    if interaction.user.id not in configurations.owner_ids:
        await interaction.followup.send(embed=Embed(title="Unauthorized", description="You must be the owner to use this command!", color=Color.red()), ephemeral=True)
        return

    await interaction.followup.send(embed=Embed(title="Received", description="Restart request received, killing docker container...", color=Color.green()), ephemeral=True)
    print(f'[+] Restart request by {interaction.user.id} ({interaction.user.display_name})')
    await client.change_presence(status=Status.dnd, activity=Game('restarting...'))
    sleep(5)
    system('kill 1')

@tree.command(name = 'whitelist_list', description ='OWNER ONLY - Get beta whitelist list in database.json', guild=Object(id=configurations.owner_guild_id))
async def whitelist_list(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    if not interaction.user.id in configurations.owner_ids:
        await interaction.followup.send(embed=Embed(title="Unauthorized", description="You must be the owner to use this command!", color=Color.red()), ephemeral=True)
        return
    
    try:
        embed = Embed(title='Whitelist list', description='Here is the list of beta-whitelisted user IDs:', color = Color.green())
        current_list = ""
        for i in get_whitelist():
            current_list += f'<@{i}> ({i})'
        embed.add_field(name='IDs', value = current_list)
        await interaction.followup.send(embed=embed, ephemeral=True)
    except Exception as e:
        print("""----------Exception in command /whitelist_list----------""")
        print(e)
        print("""----------End----------""")
        await interaction.followup.send(embed=Embed(title="Exception occurred", description=str(e), color=Color.red()), ephemeral=True)

@tree.command(name = 'whitelist_modify', description='OWNER ONLY - Get beta whitelist list in database.json', guild=Object(id=configurations.owner_guild_id))
async def whitelist_modify(interaction: Interaction, user: Member, add: bool = True):
    await interaction.response.defer(ephemeral=True)
    if not interaction.user.id in configurations.owner_ids:
        await interaction.followup.send(embed=Embed(title="Unauthorized", description="You must be the owner to use this command!", color=Color.red()), ephemeral=True)
        return
    
    try:
        update_status = update_whitelist(id = user.id, add = add)
        await interaction.followup.send(embed=Embed(title='Done', description=f'Successfully {"added" if bool else "removed"} this user in the list: {user.id} ({user.id})', color = Color.green()) if update_status else Embed(title='Failed', description='A error occured', color = Color.green()), ephemeral=True)
    except Exception as e:
        print("""----------Exception in command /whitelist_modify----------""")
        print(e)
        print("""----------End----------""")
        await interaction.followup.send(ephemeral= True, embed=Embed(title="Exception occurred", description=str(e), color=Color.red()))

@tree.command(name = 'maintenance', description='OWNER ONLY - Toggle maintenance mode for supported commands')
async def maintenance(interaction: Interaction, status_to_set: bool = False):
    await interaction.response.defer(ephemeral = True)
    if not interaction.user.id in configurations.owner_ids:
        await interaction.followup.send(embed=Embed(title="Unauthorized", description="You must be the owner to use this command!", color=Color.red()), ephemeral=True)
        return
    global maintenance_status
    old = maintenance_status
    maintenance_status = status_to_set
    await interaction.followup.send(embed=Embed(color=Color.green(), title='Success', description=f'Maintenance status changed: {old} -> {maintenance_status}'))
"""
-------------------------------------------------
FEATURE COMMANDS (beta)
-------------------------------------------------
"""
@tree.command(name='screenshot', description='Take a screenshot of a website')
async def screenshot(interaction: Interaction, url: str, window_height: int = 1920, window_width: int = 1080):
    global global_ratelimit
    await interaction.response.defer(ephemeral=True)
    # conditions to stop executing the command
    if not beta_check(user = interaction.user.id, beta_bool = configurations.beta) or not interaction.user.id in configurations.owner_ids:
        await interaction.followup.send(embed = Embed(title='Unauthorized', description='This command is in beta mode, only whitelisted user can access.'), ephemeral = True)
        return
    if interaction.guild_id is None:
        await interaction.followup.send(embed=Embed(title='Error', description='This command can only be used in a server.', color=Color.red()), ephemeral=True)
        return
    if not url.startswith('http'):
        await interaction.followup.send(embed=Embed(title='Error', description='Please provide a valid URL, including http or https.', color=Color.red()), ephemeral=True)
        return
    if global_ratelimit >= configurations.max_global_ratelimit:
        await interaction.followup.send(embed=Embed(color=Color.red(), title='Rate-limited', description='Bot is currently global rate-limited, please try again later'), ephemeral= True)
        return
    
    global_ratelimit += 1
    try:
        image_bytes = get_screenshot(url=url, window_height=window_height, window_width=window_width)
        embed = Embed(title=f'Screenshot of {url}', color=Color.green())
        embed.set_image(url='attachment://screenshot.png')
        await interaction.followup.send(embed=embed, file=File(BytesIO(image_bytes), filename='screenshot.png'), ephemeral=True)
    except Exception as e:
        print("""----------Exception in command /screenshot----------""")
        print(e)
        print("""----------End----------""")
        if interaction.user.id in configurations.owner_ids:
            await interaction.followup.send(embed=Embed(title='Exception Occurred', description=f'Exception occurred: {e}', color=Color.red()), ephemeral=True)
        else:
            await interaction.followup.send(embed = Embed(title='Error', description='Exception occurred, we are trying to fix asap', color=Color.red()), ephemeral=True)
    global_ratelimit += -1

"""
-------------------------------------------------
FEATURE COMMANDS (official)
-------------------------------------------------
"""
@tree.command(name='echo', description='Echo the provided string to the user')
async def echo(interaction: Interaction, string: str, ephemeral: bool = True):
    await interaction.response.defer(ephemeral=ephemeral)
    await interaction.followup.send(string, ephemeral=ephemeral)

"""
-------------------------------------------------
CLIENT EVENTS
-------------------------------------------------
"""
@client.event
async def on_ready():
    global global_ratelimit
    global maintenance_status
    global_ratelimit = 0
    maintenance_status = configurations.default_maintenance_status
    await client.change_presence(activity=Game('starting...'), status=Status.dnd)
    sleep(2)
    print("Syncing commands to the owner guild...")
    await tree.sync(guild=Object(id=configurations.owner_guild_id))
    print("Done! Bot is ready!")
    print(str(client.user) + ' has connected to Discord.')
    print('Connected to ' + str(len(client.guilds)) + ' guilds and ' + str(len(client.guilds)) + ' users.' )
    await client.change_presence(activity=Game('utils-bot'), status=Status.online)
"""
-------------------------------------------------
BOOT
-------------------------------------------------
"""
if __name__ == '__main__':
    ka()
    client.run(configurations.bot_token)

