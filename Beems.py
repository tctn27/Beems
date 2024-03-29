import websockets

try:
    import time
    import requests
    from discord.ext import commands
    from discord import Game
    from discord import Message
    from discord import File
    from os import listdir
    import os
    import re
    import math
    from random import randint
    from PIL import Image, ImageDraw, ImageFont

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


    def choose_without_replacement(in_list, num=8):
        """

        :type in_list: list
        :type num: int
        """
        temp = in_list

        out = []
        for i in range(num):
            member = in_list[randint(0, len(in_list) - 1)]
            out.append(member)
            temp.remove(member)
        return out


    def combine2(first_word, second_word):
        shared = []

        for count, letter in enumerate(first_word):
            for count2, letter2 in enumerate(second_word):
                if letter == letter2:
                    if count != 0 and count2 != len(second_word) - 1:
                        shared.append((letter, count + 1, count2))

        if not shared:
            return combine(first_word, second_word)

        distanced = []
        mid1, mid2 = len(first_word) / 2, len(second_word) / 2
        for letter in shared:
            distanced.append((letter, math.pow(letter[1] - mid1, 2) + math.pow(letter[2] - mid2, 2)))

        distanced.sort(key=lambda x: (x[1], math.pow(x[0][1] - x[0][2], 2)))
        chosen = distanced[0][0]

        word = first_word[0:chosen[1]:] + second_word[chosen[2] + 1:]

        return word


    def eid(n1, n2, n3, n4):
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
        vowels = ["a", "e", "i", "o", "u", "y"]
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
        for letter in second_word:
            letter_index += 1
            if letter in vowels:
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

        choice = randint(0, 1)
        combined = None
        if choice == 0:
            combined = combine(set_of_two[0], set_of_two[1])
        elif choice == 1:
            combined = combine2(set_of_two[0], set_of_two[1])

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
        except ValueError:
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

                elif message.content.startswith("~addBingo"):
                    inp = message.content.split("~addBingo")[1].strip()
                    with open("bingo_tiles", "a") as file:
                        file.writelines(inp + "\n")
                        file.close()
                    await message.channel.send("Successfully added")

                elif message.content.startswith("~bingo"):
                    inp = message.content.split("~bingo")[1].strip()
                    try:
                        size = int(re.match("(\d)", inp).groups()[0])
                    except:
                        size = 3

                    tiles = []
                    with open("bingo_tiles", "r+") as file:
                        for line in file:
                            tiles.append(line.rstrip())

                    img = Image.new('RGB', (300 * size, 300 * size))

                    d = ImageDraw.Draw(img)

                    for x in range(size):
                        d.line([(300 * (x+1), 0), (300 * (x+1), 300 * (size+1))], width=2)
                    for y in range(size):
                        d.line([(0, 300 * (y+1)), (300 * (size+1), 300 * (y+1))], width=2)

                    chosen_list = []
                    if size%2:
                        chosen_list = choose_without_replacement(tiles, num=(size*size)-1)
                        chosen_list.insert(4, "Free\nSpace")
                    else:
                        chosen_list = choose_without_replacement(tiles, num=size*size)

                    fnt = ImageFont.truetype("arial.ttf", 24)
                    for y in range(size):
                        for x in range(size):
                            phrase = chosen_list[size * y + x]
                            out_phrase = phrase
                            w, h = d.textsize(out_phrase, fnt)
                            splits = 1

                            while w > 250:
                                out_phrase = ""
                                spaces = []
                                for index, letter in enumerate(phrase):
                                    if letter == " ":
                                        spaces.append(index)
                                last_point = 0
                                for line in range(splits):
                                    if line > 0:
                                        cut_point = spaces[math.floor(len(spaces)*line/(splits+1))]
                                        out_phrase += phrase[:cut_point] + "\n"
                                        last_point = cut_point
                                out_phrase += phrase[last_point + 1:]
                                w, h = d.textsize(out_phrase, fnt)
                                splits += 1

                            d.text((x * 300 + 150 - w / 2, y * 300 + 150 - h / 2), out_phrase, font=fnt,
                                   color=(125, 125, 125))

                    ImageDraw.Draw(img)

                    img.save("bingo.png", "PNG")

                    await message.channel.send(file=File('bingo.png'))

                elif message.content.startswith("~MCIP"):
                    ip = requests.get('https://api.ipify.org').text
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

                    for i in eid(nums[0], nums[1], nums[2], nums[3]):
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
                                            await message.channel.send(
                                                "Too many dice, what the hell are you doing mate")
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
                    elif len(words) > 0 and randint(0, 20) == 0:
                        await full_combine(message, words)
            except Exception as e:
                print(e)
                await message.channel.send("<@227336569881624576> error\n" + str(e))


    client.run(TOKEN)
except websockets.ConnectionClosed as e:
    os.system("runbot")
