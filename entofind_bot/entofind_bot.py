import discord
import re
import os
import requests
import json

#Configs discord intents then uses makes a client connection
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

emoji_dict = {
    "0dust": "<:0dust:1552134153838010488>",
    "1dust": "<:1dust:1552134868027187210>",
    "2dust": "<:2dust:1552134869557973024>",
    "3dust": "<:3dust:1552134870334046279>",
    "4dust": "<:4dust:1552134871432831116>",
    "5dust": "<:5dust:1552134872456364062>",
    "6dust": "<:6dust:1552134874033426512>",
    "7dust": "<:7dust:1552134875249774762>",
    "8dust": "<:8dust:1552134876097151037>",
    "10dust": "<:10dust:1552134877317570630>",
    "Ldust": "<:Ldust:1552134878110285824>",
    "Mdust": "<:Mdust:1552134878827388998>",
    "Sdust": "<:Sdust:1552134880123687003>",
    "Tdust": "<:Tdust:1552134880933056512>",
    "Xdust": "<:Xdust:1552134881931173908>",
    "Exhaust": "<:exhaust:1552172370872115270>"
}
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    text = message.content
    if re.findall("\\[\\[([^\\]]+)\\]\\]", text):
        #Iterates through the message, where it grabs a string of text enclosed in two square brackets, then continues to iterate over the message with the start at the end of the first found string
        loop = True
        names = []
        while loop:
            search = re.search(f"\\[\\[([^\\]]+)\\]\\]", text)
            if (search):
                span = search.span()
                name = search.group().replace("[", "").replace("]", "").replace("’", "'").replace("“", '"')
                names.append(name)
                text = text[span[1]:len(text)]
            else:
                loop = False
        
        for item in names:
            #Queries the API for information on cards with the name provided in the string
            response = requests.get("http://api.entofind.com/cards/card_name", params=({'name':f'{item}'}))

            #The API returns a string response if multiple cards are found with that name. This accounts for that and sends that response as a message
            if (response.status_code == 300):
                await message.channel.send("More than one card found, try narrowing your search.")
            elif (response.status_code == 400):
                await message.channel.send("No card found.")
            else:
                card_info = response.json()

                #Put information from the JSON returned into variables for parsing on the embed
                id = card_info["id"]
                card_name = card_info["name"]
                dust = card_info["dust"]
                supertype = card_info["supertype"]
                subtype = card_info["subtype"]
                attack = card_info["attack"]
                defense = card_info["defense"]
                devotion_value = card_info["devotion_value"]
                trait = card_info["trait"]
                resist = card_info["resist"]
                rules_text = card_info["rules_text"]
                flavor_text = card_info["flavor_text"]
                equip_dust = card_info["equip_dust"]
                equip_restrict = card_info["equip_restriction"]


                #Creates a title that is the name followed by a space plus the valid emojis for the card's dust
                embed_title = ""
                embed_title = embed_title + card_name + " " #Add the name

                if dust:
                    #Initializes the values of the different varieties of dust symbols
                    numeric_symbols = ""
                    letter_symbols = ""
                    for dust_symbol in dust:
                        if (dust_symbol.isnumeric()):
                            numeric_symbols = numeric_symbols + dust_symbol
                        else:
                            letter_symbols = letter_symbols + dust_symbol

                    #Treats the numeric symbols as 1 object (to account for double digits) then adds the corresponding emoji
                    if numeric_symbols:
                        embed_title = embed_title + emoji_dict[f"{numeric_symbols}dust"]

                    #Goes through each non-numeric value of the dust cost and adds the appropriate emoji
                    for letter_symbol in letter_symbols:
                        letter_symbol = letter_symbol.upper()
                        embed_title = embed_title + emoji_dict[f"{letter_symbol}dust"]
                
                

                #Parses the supertype, subtype, textbox, flavor text, atk/def, devotion, and traits of the card to become the description
                embed_description = ""

                #Adds supertype and subtype
                if ((supertype) and (subtype)):
                    embed_description = embed_description + supertype + " - " + subtype + " \n "

                #Adds the rules text
                if (rules_text): 
                    #Replaces all instances of dust symbols with the appropriate emoji
                    rules_text = rules_text.replace("{0}", emoji_dict["0dust"])
                    rules_text = rules_text.replace("{1}", emoji_dict["1dust"])
                    rules_text = rules_text.replace("{2}", emoji_dict["2dust"])
                    rules_text = rules_text.replace("{3}", emoji_dict["3dust"])
                    rules_text = rules_text.replace("{4}", emoji_dict["4dust"])
                    rules_text = rules_text.replace("{5}", emoji_dict["5dust"])
                    rules_text = rules_text.replace("{6}", emoji_dict["6dust"])
                    rules_text = rules_text.replace("{7}", emoji_dict["7dust"])
                    rules_text = rules_text.replace("{8}", emoji_dict["8dust"])
                    rules_text = rules_text.replace("{10}", emoji_dict["10dust"])
                    rules_text = rules_text.replace("{L}", emoji_dict["Ldust"])
                    rules_text = rules_text.replace("{M}", emoji_dict["Mdust"])
                    rules_text = rules_text.replace("{S}", emoji_dict["Sdust"])
                    rules_text = rules_text.replace("{T}", emoji_dict["Tdust"])
                    rules_text = rules_text.replace("{X}", emoji_dict["Xdust"])
                    rules_text = rules_text.replace("{E}", emoji_dict["Exhaust"])


                    embed_description = embed_description + rules_text + " \n "


                #Adds the equip information if it exists:
                if ((equip_dust is not None) or equip_restrict):
                    embed_description = embed_description + "Equip "

                    #Adds dust symbols of the equip cost if it has one
                    if (equip_dust is not None):
                        #Initializes the values of the different varieties of dust symbols
                        numeric_symbols = ""
                        letter_symbols = ""
                        for dust_symbol in equip_dust:
                            if (dust_symbol.isnumeric()):
                                numeric_symbols = numeric_symbols + dust_symbol
                            else:
                                letter_symbols = letter_symbols + dust_symbol

                        #Treats the numeric symbols as 1 object (to account for double digits) then adds the corresponding emoji
                        if numeric_symbols:
                            embed_description = embed_description + emoji_dict[f"{numeric_symbols}dust"]

                        #Goes through each non-numeric value of the dust cost and adds the appropriate emoji
                        for letter_symbol in letter_symbols:
                            letter_symbol = letter_symbol.upper()
                            embed_description = embed_description + emoji_dict[f"{letter_symbol}dust"]

                        #Adds the ending of the line if it doesn't have a equip restriction
                        if (equip_restrict is None):
                            embed_description = embed_description + ". \n "

                    #Adds the equip restriction if it has one
                    if equip_restrict:
                        #Adds a trailing space for flow
                        if equip_dust:
                            embed_description = embed_description + " "
                        embed_description = embed_description + "to " + equip_restrict + ". \n "

                        

                #Adds the flavor text
                if (flavor_text):
                    embed_description = embed_description + "*" + flavor_text + "* \n "

                #Adds atk, def, dev
                if ((attack is not None) and (defense is not None) and (devotion_value is not None)):
                    embed_description = embed_description + attack + "/" + defense + " • " + str(devotion_value) + " Devotion \n "

                #Adds atk, def, dev
                if ((trait) and (resist)):
                    embed_description = embed_description + trait + "/" + resist
                    








                embed = discord.Embed(
                    title=embed_title, 
                    colour=discord.Colour(0x80063e), 
                    url=f"https://entofind.com/card.php?card_id={id}", 
                    description=embed_description)

                embed.set_thumbnail(url=f"https://entofind.com/img/card_img/png/{id}.png")

                await message.channel.send(content=f"https://entofind.com/card.php?card_id={id}", embed=embed)








client.run(os.environ.get("Discord_Token"))


