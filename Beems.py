import websockets

try:
    import random
    import time
    from discord.ext import commands
    from discord import Game
    from discord import Message
    from os import listdir
    import os

    with open("beems_token", "r") as file:
        TOKEN = file.read()

    client = commands.Bot(command_prefix="~")

    whitelist = []
    with open("whitelist", "r+") as f:
        for i in f:
            whitelist.append(int(i))

    blacklist = []
    with open("blacklist", "r+") as f:
        for i in f:
            blacklist.append(int(i))


    def only_letters(word):
        letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
                   "u", "v", "w", "x", "y", "z"]
        word = word.lower()
        for letter in word:
            if letter not in letters:
                return False
        return True


    def combine(first_word, second_word):
        vowels = ["a", "e", "i", "o", "u"]
        out_word = ""

        first = True
        for letter_index in first_word:
            if first:
                out_word += letter_index
                first = False
            else:
                if letter_index not in vowels:
                    out_word += letter_index
                else:
                    break

        letter_index = -1
        for l in second_word:
            letter_index += 1
            if l in vowels:
                out_word += second_word[letter_index:]
                return out_word

        return out_word


    def give_eligible_words(sentence):
        raw_words = sentence.content.lower().split(" ")
        words = []
        long = 3
        eligible_words = []
        was_long = False
        buffer = ""

        for word in raw_words:
            if only_letters(word):
                words.append(word)
            else:
                words.append("")

        for word in words:
            if len(word) >= long and was_long:
                eligible_words.append([buffer, word])
                buffer = word
            elif len(word) >= long:
                buffer = word
                was_long = True
            else:
                was_long = False

        return eligible_words


    def store_meme(message):
        with open(".\\memes\\" + str(time.time()), "a+") as storage_file:
            storage_file.write(message)


    def get_meme():
        file_list = listdir(".\\memes\\")
        fetch_file = file_list[random.randint(0, len(file_list) - 1)]
        with open("memes/" + fetch_file, "r+") as fetch_file:
            return str(fetch_file.read())


    async def full_combine(message, words):
        set_of_two = words[random.randint(0, len(words) - 1)]
        combined = combine(set_of_two[0], set_of_two[1])
        await message.channel.send("*" + combined + "*")


    # noinspection PyArgumentList
    def uwuified(message=str):
        message = message.lower()
        message = message.replace("er ", "a ")
        message = message.replace("'re", "'a")
        message = message.replace("r", "w")
        message = message.replace("l", "w")
        message = message.replace("th ", "f ")
        message = message.replace(" th", " d")
        message = message.replace("tion", "shun")
        return message


    @client.event
    async def on_ready():
        await client.change_presence(activity=Game(name="~help for help"))
        pass


    @client.event
    async def on_message(message):
        if not message.author.id == 585050654330847232:
            if message.channel not in blacklist:
                try:
                    if message.content.startswith("~update") and message.channel.id in whitelist:  # direct calls
                        await message.channel.send("Update inbound, shutting down momentarily")
                        os.system("update")
                    elif message.content.startswith("~uwu"):
                        await message.channel.send(uwuified(message.content.split("~uwu")[1].strip()) + "\nuwu")
                    elif message.content.startswith("~save"):
                        store_meme(message.content.split("~save"))
                        await message.channel.send("Meme stored")
                    elif message.content.startswith("~blacklist"):
                        if message.content == "~blacklist":
                            with open("blacklist", "a") as file:
                                file.write(message.channel.id + "\n")
                        else:
                            with open("blacklist", "a") as file:
                                file.write(message.content.split("~blacklist ") + "\n")
                    elif message.content.startswith("@Beems"):
                        words = give_eligible_words(message)
                        await message.channel.send(full_combine(message, words))
                    elif message.content.startswith("~meme"):
                        await message.channel.send(get_meme())
                    elif message.content == "~help":
                        await message.channel.send("**Commands for Beems!**\n"
                                                   "\n"
                                                   "ping: test the latency of Beems\n"
                                                   "~uwu [message]: uwuifies the message\n"
                                                   "    Also has a 1/100 chance of happening on any message\n"
                                                   "Beems also has a 1/10 chance of combining 2 words in any given "
                                                   "sentence\n "
                                                   "@Beems: combines two words in the remainder of the message if "
                                                   "possible\n"
                                                   "~link: shows the link to add Beems to your other servers\n"
                                                   "~blacklist: stops Beems from looking at "
                                                   "\n"
                                                   "**Memes**\n"
                                                   "\n"
                                                   "e\n"
                                                   "modok\n"
                                                   "x")
                    elif message.content.startswith("~link"):
                        await message.channel.send("Please follow this link to add Beems to your "
                                                   "servers:\nhttps://discordapp.com/oauth2/authorize?client_id"
                                                   "=585050654330847232&scope=bot&permissions=8")
                    elif message.content == "e" or message.content == "E":
                        await message.channel.send("https://i.kym-cdn.com/entries/icons/original/000/026/008"
                                                   "/Screen_Shot_2018-04-25_at_12.24.22_PM.png")
                    elif "modok" in message.content.lower() or "M.O.D.O.K." in message.content.upper():
                        await message.channel.send("https://vignette.wikia.nocookie.net/assistme/images/9/92/Modok.png"
                                                   "/revision/latest?cb=20120710014024")
                    elif message.content == "x" or message.content == "X":
                        await message.channel.send("https://i.kym-cdn.com/entries/icons/original/000/023/021"
                                                   "/e02e5ffb5f980cd8262cf7f0ae00a4a9_press-x-to-doubt-memes-memesuper-la"
                                                   "-noire-doubt-meme_419-238.png")
                    elif message.content == "bruh":
                        await message.channel.send("bruh")
                    elif "stuff" in message.content and random.randint(0, 10) == 0:
                        await message.channel.send("I'm stuff <:imstuff:610620140052283393>")
                    elif message.content == "ping":
                        await message.channel.send("pong")

                    # randomised things
                    if "http" in message.content:  # don't mess with links
                        pass
                    elif random.randint(0, 100) <= 2 and message.content.strip().lower() != uwuified(
                            (message.content.strip())):
                        await message.channel.send(uwuified(message.content.strip()) + "\nuwu")
                    else:
                        words = give_eligible_words(message)
                        if len(words) > 0 and message.channel in whitelist:
                            full_combine(message, words)
                        elif len(message.content.split(" ")) == 2 and len(words) > 0 \
                                and message.channel.id in whitelist:
                            full_combine(message, words)
                        elif len(words) > 0 and random.randint(0, 20) == 0:
                            full_combine(message, words)
                except Exception as e:
                    with open("logs/" + str(time.time()) + ".log", "w+") as log_file:
                        log_file.write(str(time.time()) + "\n")
                        log_file.write(str(e))
                    await message.channel.send("<@227336569881624576> <@191357391453945856> error")

    client.run(TOKEN)
except websockets.exceptions.ConnectionClosed as e:
    os.system("runbot")
