import subprocess

import websockets

try:
    import time
    from discord.ext import commands
    from discord import Game
    from discord import Message
    from os import listdir
    import os
    import re
    from random import randint

    with open("beems_token", "r+") as file:
        TOKEN = file.read().rstrip()

    client = commands.Bot(command_prefix="~")

    whitelist = []
    with open("whitelist", "r+") as f:
        for i in f:
            whitelist.append(int(i))

    blacklist = []
    with open("blacklist", "r+") as f:
        for i in f:
            blacklist.append(int(i))


    def EID(n1, n2, n3, n4):
        numbers = [n1, n2, n3, n4]
        keywords = ["flying", "deathtouch", "reach", "indestructible", "defender", "lifelink", "trample", "menace",
                    "first strike", "double strike", "haste", "hexproof"]
        copy = ["flying", "deathtouch", "reach", "indestructible", "defender", "lifelink", "trample", "menace",
                "first strike", "double strike", "haste", "hexproof"]
        out = []
        current_number = 0
        iteration = 0
        for word in keywords:
            a1 = numbers[iteration % len(numbers)]
            a2 = numbers[(iteration + 1) % len(numbers)]
            current_number = (current_number * a1) + a2
            selected = copy[current_number % len(copy)]

            out.append((word, selected))
            copy.remove(selected)

        return out


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
        fetch_file = file_list[randint(0, len(file_list) - 1)]
        with open("memes/" + fetch_file, "r+") as fetch_file:
            return str(fetch_file.read())


    async def full_combine(message, words):
        set_of_two = words[randint(0, len(words) - 1)]
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


    async def blacklist_on_call(message):
        await message.channel.send("React with 👍 to confirm")

        def check(reaction, user):
            return user == message.author and str(reaction.emoji) == '👍'

        try:
            reaction, user = await client.wait_for("reaction_add", timeout=60.0, check=check)
        except:
            await message.channel.send("Channel not blacklisted")
        else:
            with open("blacklist", "w+") as file:
                file.write("\n" + message.channel.id)
            await message.channel.send("Channel blacklisted")


    @client.event
    async def on_ready():
        print("ready")
        await client.change_presence(activity=Game(name="~help for help"))
        pass


    @client.event
    async def on_message(message):
        if not message.author.id == 585050654330847232 and message.channel not in blacklist:
            try:
                if message.content.startswith("~update") and message.channel.id in whitelist:  # direct calls
                    await message.channel.send("Update inbound, shutting down momentarily")
                    os.system("update")

                elif message.content.startswith("~MCIP"):
                    ip = subprocess.check_output(['curl https://ipinfo.io/ip'])
                    await message.channel.send(ip)

                elif message.content.startswith("~EID"):
                    inp = message.content.split("~EID")[1].strip()
                    cap = re.match("(\d\d\d\d)", inp)
                    nums = []
                    if cap is not None:
                        for i in cap.groups()[0]:
                            nums.append(int(i))
                        out = "For " + cap.groups()[0] + ":\n\n"
                    else:
                        nums = [randint(1, 6), randint(1, 6), randint(1, 6), randint(1, 6)]
                        out = "For " + str(nums[0]) + str(nums[1]) + str(nums[2]) + str(nums[3]) + ":\n\n"

                    for i in EID(nums[0], nums[1], nums[2], nums[3]):
                        out += i[0].capitalize() + " is " + i[1] + "\n"

                    await message.channel.send(out)

                elif message.content.startswith("~roll"):
                    inp = message.content.split("~roll")[1].strip()
                    capture = re.findall("(\d*)[d](\d+)([+-])?(\d*)(adv|dis)?|\s([+-])\s|(dc\d+)", inp)

                    if not capture:
                        await message.channel.send("Invalid roll input\n"
                                                   "It needs to look something like\n"
                                                   "~roll 2d6adv - 3d2+1dis")
                    else:
                        first = True
                        polarity = True
                        total = 0
                        overall_string = ""
                        dc = -1
                        for group in capture:
                            if group[6] == '':
                                if group[5] == '':
                                    if group[1] != "0":
                                        if int(group[0]) <= 300:
                                            rolling_sum = 0
                                            rolls = []
                                            if group[4] == 'adv':
                                                if group[0] == '' or group[0] == '1':
                                                    roll1 = randint(1, int(group[1]))
                                                    roll2 = randint(1, int(group[1]))
                                                    rolls.append([roll1, roll2])
                                                    rolling_sum += max(roll1, roll2)
                                                else:
                                                    for i in range(0, int(group[0])):
                                                        roll1 = randint(1, int(group[1]))
                                                        roll2 = randint(1, int(group[1]))
                                                        rolls.append([roll1, roll2])
                                                        rolling_sum += max(roll1, roll2)

                                                if group[3] != "":
                                                    if group[2] == "+":
                                                        rolling_sum += int(group[3])
                                                    elif group[2] == "-":
                                                        rolling_sum -= int(group[3])
                                            elif group[4] == 'dis':
                                                if group[0] == '' or group[0] == '1':
                                                    roll1 = randint(1, int(group[1]))
                                                    roll2 = randint(1, int(group[1]))
                                                    rolls.append([roll1, roll2])
                                                    rolling_sum += min(roll1, roll2)
                                                else:
                                                    for i in range(0, int(group[0])):
                                                        roll1 = randint(1, int(group[1]))
                                                        roll2 = randint(1, int(group[1]))
                                                        rolls.append([roll1, roll2])
                                                        rolling_sum += min(roll1, roll2)

                                                if group[3] != "":
                                                    if group[2] == "+":
                                                        rolling_sum += int(group[3])
                                                    elif group[2] == "-":
                                                        rolling_sum -= int(group[3])
                                            else:
                                                if group[0] == '':
                                                    roll = randint(1, int(group[1]))
                                                    rolls.append(roll)
                                                    rolling_sum += roll
                                                else:
                                                    for i in range(0, int(group[0])):
                                                        roll = randint(1, int(group[1]))
                                                        rolls.append(roll)
                                                        rolling_sum += roll

                                                if group[3] != "":
                                                    if group[2] == "+":
                                                        rolling_sum += int(group[3])
                                                    elif group[2] == "-":
                                                        rolling_sum -= int(group[3])

                                            string = ""
                                            if first:
                                                first = False
                                            else:
                                                if polarity:
                                                    string += "\n+\n"
                                                else:
                                                    string += "\n-\n"
                                            for i in rolls:
                                                string += str(i)
                                                string += " + "
                                            if group[2] == '':
                                                string = string[:-3]
                                            elif group[2] == "-":
                                                string = string[:-3] + " - "
                                                string += str(group[3])
                                            else:
                                                string += str(group[3])

                                            string += " = " + str(rolling_sum)

                                            if polarity:
                                                total += rolling_sum
                                            else:
                                                total -= rolling_sum

                                            overall_string += string
                                        else:
                                            await message.channel.send("Too many dice, what the hell are you doing mate")
                                    else:
                                        await message.channel.send("Dice don't have 0 sides, silly billy")
                                else:
                                    if group[5] == "-":
                                        polarity = not polarity
                                    if group[5] == "+":
                                        polarity = True

                            else:
                                dc = int(group[6][2:])

                        overall_string += "\nTotal: " + str(total)
                        if dc != -1:
                            overall_string += "\nDC: " + str(dc)
                            if total >= dc:
                                overall_string += "\nResult: Passed"
                            else:
                                overall_string += "\nResult: Failed"
                        await message.channel.send(overall_string)

                elif message.content.startswith("~uwu"):
                    await message.channel.send(uwuified(message.content.split("~uwu")[1].strip()) + "\nuwu")

                elif message.content.startswith("~d10k"):
                    inp1 = message.content
                    inp = inp1.split("~d10k")
                    if inp[1] == "":
                        num = randint(0, 9999)
                        with open("d10k.txt", "r+", encoding='utf-8-sig') as file:
                            for i, line in enumerate(file):
                                if i == num:
                                    await message.channel.send(line)
                                elif i > num:
                                    break
                    else:
                        try:
                            num = int(re.search("(\d\d\d\d)", inp[1]).groups()[0])
                            with open("d10k.txt", "r+", encoding='utf-8-sig') as file:
                                for i, line in enumerate(file):
                                    if i == num:
                                        await message.channel.send(line)
                                    elif i > num:
                                        break
                        except AttributeError:
                            await message.channel.send("Needs to be in the form ~d10k XXXX")

                elif "beems" in message.content.lower():
                    await message.add_reaction("🅱️")

                elif message.content.startswith("<@!585050654330847232>"):
                    words = give_eligible_words(message)
                    await full_combine(message, words)

                elif message.content.startswith("~initiative"):
                    os.system("runInitiative")
                    await message.channel.send("Site started at 192.168.1.112:5000")

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
                                               "~blacklist: stops Beems from looking at this channel"
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
                elif "stuff" in message.content and randint(0, 10) == 0:
                    await message.channel.send("I'm stuff <:imstuff:610620140052283393>")
                elif message.content == "ping":
                    await message.channel.send("pong")

                # randomised things
                if "http" in message.content:  # don't mess with links
                    pass
                # elif random.randint(0, 100) <= 1 and message.content.strip().lower() != uwuified(
                #        (message.content.strip())):
                #    await message.channel.send(uwuified(message.content.strip()) + "\nuwu")
                else:
                    words = give_eligible_words(message)
                    if len(words) > 0 and message.channel in whitelist:
                        await full_combine(message, words)
                    elif len(message.content.split(" ")) == 2 and len(words) > 0 \
                            and message.channel.id in whitelist:
                        await full_combine(message, words)
                    elif len(words) > 0 and randint(0, 50) == 0:
                        await full_combine(message, words)
            except Exception as e:
                print(e)
                await message.channel.send("<@227336569881624576> error\n" + str(e))


    client.run(TOKEN)
except websockets.exceptions.ConnectionClosed as e:
    os.system("runbot")
