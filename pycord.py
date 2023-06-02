import datetime
import os.path
import discord
from datetime import datetime
from discord.ext import commands

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

description = "auf ganz weird angelehnt"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description=description,
    intents=intents,
)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

 
creds = Credentials.from_authorized_user_file('token.json', SCOPES)
if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

@bot.command()
async def kalender(ctx: commands.Context):

    ## alle nächsten Events auslesen
    
    embed = discord.Embed(title="Vorstehende Erinnerungen")
    service = build('calendar', 'v3', credentials=creds)
    # Call the Calendar API
    now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        embed.add_field(name='error', value="es gibt keine kommenden Erinnerungen")
        await ctx.reply(embed=embed)
        return

    # Prints the start and name of the next 10 events
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        embed.add_field(name=event['summary'], value=start, inline=False)
    await ctx.reply(embed=embed)

@bot.command()   
async def add(ctx: commands.Context, name: str, date: str, description: str):
    service = build('calendar', 'v3', credentials=creds)
    try:
        event_date = datetime.strptime(date, "%d/%m/%y").date()
        print(event_date.isoformat())
    except ValueError:
        print(ValueError)
        embed = discord.Embed(title="Error")
        embed.add_field(name="Falsches Format", value='Bitte nutz das: !add "<name>" <d/m/y> "<beschreibung>"')
        await ctx.reply(embed=embed)
        return

    event = {
        'summary': name,
        'description': description,
        'start': {
            'dateTime': event_date.isoformat(),
            'timeZone': 'Europe/Berlin'
        },
        'end': {
            'dateTime': event_date.isoformat(),
            'timeZone': 'Europe/Berlin'
        }
    }

    try:
        service.events().insert(calendarId='primary', body=event).execute()
        embed = discord.Embed(title='Event Added')
        embed.add_field(name=name, value=date)
        await ctx.reply(embed=embed)
    except HttpError as e:
        error_message = e._get_reason()
        embed = discord.Embed(title='Error')
        embed.add_field(name='Failed to Add Event', value=error_message)
        await ctx.reply(embed=embed)

        
    
bot.run("MTExMzQwODUyOTU0NjYyNTEzNQ.GGvsCS.d0sNdc7UO_kuP0v7GlIZTOJHAPjcOerfNcR88M")