import os
from keep_alive import keep_alive
from api import Database
from discord.ext import commands
import settings
import discord
from datetime import date
import random
import time

inte = discord.Intents.default()
inte.messages = True
inte.message_content = True
inte.members = True

bot = commands.Bot(
    command_prefix=settings.bot_prefix,  # Change to desired prefix
    case_insensitive=True,  # Commands aren't case-sensitive
    intents=inte,
    help_command=None
)

bot.author_id = 1102272783712522331  # Change to your discord id!!!

database = Database()
guild = None


@bot.event
async def on_ready():  # When the bot is ready
    global guild
    guild = bot.get_guild(settings.guild_id)
    await bot.change_presence(status=discord.Status.online)
    print("logged in as {0.user}".format(bot))


# @bot.event
async def on_message(ctx):
    if not ctx.channel.id == 842522103315169320:
        await eggy_check(ctx, True)

    await bot.process_commands(ctx)


@bot.command("help")
async def help(ctx, page: int = 1):
    emb = discord.Embed(
        title="commands"
    )

    if bot.get_guild(settings.guild_id).get_role(settings.staff_role) in ctx.author.roles:
        if page == 1:
            emb.description = "**Announce**\nMake an announcement for everyone to see\n\n" \
                              "**Basket**\nShow you all the eggs you have\n\n" \
                              "**Buy**\nBuy something from the market\n\n" \
                              "**Crack**\nCrack an egg open to get egg yolks (**Requires Egg Topper**)\n\n" \
                              "**Dig**\nDig up some eggs (**Requires Delicate Shovel or Golden Shovel**)\n\n" \
                              "**Dupe**\nDo what science cant and clone some eggs\n\n"
            emb.set_footer(text="page 1/3")
        elif page == 2:
            emb.description = "**Harvest**\nHarvest the eggs that the chickens laid\n\n" \
                              "**Help**\nShow this list\n\n" \
                              "**Hunt**\nTry and see if you can find some eggs lying around\n\n" \
                              "**Inventory**\nShow you all the items you own\n\n" \
                              "**Nick**\nTake some eggs from someone" \
                              "**Pay**\nGive the previously taken eggs back"
            emb.set_footer(text="page 2/3")
        elif page == 3:
            emb.description = "**Profile**\nShow some more information about your farm\n\n" \
                              "**Shop**\nGo visit the store\n\n" \
                              "**Share**\nShare some eggs with your friends"
            emb.set_footer(text="page 3/3")
    else:
        if page == 1:
            emb.description = "**Basket**\nShow you all the eggs you have\n\n" \
                              "**Buy**\nBuy something from the market\n\n" \
                              "**Crack**\nCrack an egg open to get egg yolks (**Requires Egg Topper**)\n\n" \
                              "**Dig**\nDig up some eggs (**Requires Delicate Shovel or Golden Shovel**)\n\n" \
                              "**Dupe**\nDo what science cant and clone some eggs\n\n" \
                              "**Harvest**\nHarvest the eggs that the chickens laid\n\n"
            emb.set_footer(text="page 1/2")
        elif page == 2:
            emb.description = "**Help**\nShow this list\n\n" \
                              "**Hunt**\nTry and see if you can find some eggs lying around\n\n" \
                              "**Inventory**\nShow you all the items you own\n\n" \
                              "**Profile**\nShow some more information about your farm\n\n" \
                              "**Shop**\nGo visit the store\n\n" \
                              "**Share**\nShare some eggs with your friends"
            emb.set_footer(text="page 2/2")

    await ctx.channel.send(embed=emb)


@bot.command("announce")
@commands.has_role(842686615092199444)
async def announce(ctx, *, args):
    achannel = bot.get_channel(settings.announce_channel_id)
    splits = args.split("|")

    if len(splits) <= 1:
        await ctx.channel.send(
            "wrong use! {0}announce (title)|(announcement)|(?banner). yes the '|' is neccesary".format(
                settings.bot_prefix))
        return

    argument = splits[0]
    announcement = splits[1]

    if len(splits) == 3:
        banner = splits[2]
    else:
        banner = None

    emb = discord.Embed(
        title=argument,
        description=announcement
    )

    emb.set_image(url=banner)

    current_time = date.today()

    emb.set_footer(text=str(current_time),
                   icon_url="https://cdn.discordapp.com/attachments/1121483496435753100/1121495423580901386/image0.gif")

    await achannel.send(embed=emb)


@announce.error
async def announce_error(ctx, error):
    await error_handling(ctx, error, "announce")


@bot.command("basket", aliases=["eggs"])
async def basket(ctx):
    await eggy_check(ctx, False)
    authorID = ctx.author.id
    u = database.get_user(authorID)
    desc = "You currently have" + "\n<:eggy:1121872437055869048> {0} {1}".format(u.cash,
                                                                                 settings.cash_name) + "\n<:silvereggy:1122255924669726800> {0} {1}".format(
        u.ironcash, settings.iron_cash_name) + "\n<:goldeneggy:1121874261649399879> {0} {1}".format(u.goldcash,
                                                                                                    settings.gold_cash_name) + "\n<:eggyolk:1121874358730772600> {0} {1}".format(
        u.eggyolks, settings.yolk_cash_name)
    emb = discord.Embed(
        description=desc
    )

    emb.set_author(name="{0}'s Egg Basket".format(ctx.author.name),
                   icon_url="https://cdn.discordapp.com/attachments/1121483496435753100/1121876394905981069/download__2_-removebg-preview.png")

    await ctx.channel.send(embed=emb)


@bot.command("transfer", aliases=["share"])
async def transfer(ctx, target: discord.Member, amount: int):
    await eggy_check(ctx, False)
    authorID = ctx.author.id
    targetID = target.id
    if database.get_user(authorID).cash >= amount:
        database.give_cash(authorID, -amount)
        database.give_cash(targetID, amount)
        emb = discord.Embed(
            title="success",
            description="successfully shared {3} {0} {1} with {2}".format(amount, settings.cash_name, target,
                                                                          settings.eggy_emoji)
        )

        emb.set_author(name="Egg Basket",
                       icon_url="https://cdn.discordapp.com/attachments/1121483496435753100/1121876394905981069/download__2_-removebg-preview.png")
        emb.set_footer(text=str(date.today()))

        await ctx.channel.send(embed=emb)
    else:
        await ctx.channel.send("you dont have enough {0} to share with @{1}".format(settings.cash_name, targetID))


@transfer.error
async def transfer_error(ctx, error):
    await error_handling(ctx, error, "transfer")


@bot.command("harvest")
@commands.cooldown(1, settings.harvest_cooldown, commands.BucketType.user)
async def harvest(ctx):
    await eggy_check(ctx, False)
    authorID = ctx.author.id
    u = database.get_user(authorID)
    if u.farm_level == 1:
        earned = random.randint(settings.level_1_farm_min, settings.level_1_farm_max)
    elif u.farm_level == 2:
        earned = random.randint(settings.level_2_farm_min, settings.level_2_farm_max)
    elif u.farm_level == 3:
        earned = random.randint(settings.level_3_farm_min, settings.level_3_farm_max)
    elif u.farm_level == 4:
        earned = random.randint(settings.level_4_farm_min, settings.level_4_farm_max)
    elif u.farm_level == 5:
        earned = random.randint(settings.level_5_farm_min, settings.level_5_farm_max)
    else:
        await ctx.channel.send("looks like you have a bugged farm level please contact @crystalcoding_!")
        return

    if database.has_inventory(authorID, "golden chicken"):
        earned *= 1.5
        earned = round(earned, 0)

    emb = discord.Embed(
        description="successfully harvested {2} {0} {1}".format(earned, settings.cash_name, settings.eggy_emoji)
    )

    emb.set_author(name="Egg Basket",
                   icon_url="https://cdn.discordapp.com/attachments/1121483496435753100/1121876394905981069/download__2_-removebg-preview.png")

    database.give_cash(authorID, earned)
    await ctx.channel.send(embed=emb)


@harvest.error
async def harvest_error(ctx, error):
    await error_handling(ctx, error, "harvest")


@bot.command("shop", aliases=["store", "market"])
async def shop(ctx, store: str = "list"):
    await eggy_check(ctx, False)
    authorID = ctx.author.id
    if store == "economy" or store == "eco" or store == "e":
        emb = discord.Embed(
            title=None,
        )

        flevel = database.get_user(authorID).farm_level
        cost = settings.level_2_unlock_cost
        if flevel == 1:
            cost = settings.level_2_unlock_cost
        elif flevel == 2:
            cost = settings.level_3_unlock_cost
        elif flevel == 3:
            cost = settings.level_4_unlock_cost
        elif flevel == 4:
            cost = settings.level_5_unlock_cost

        if flevel != 5:
            fl_desc = "{3}**Farm Upgrade**: {1} {2}\nUpgrade your farm to level {0}".format((flevel + 1), cost,
                                                                                            settings.eggy_emoji,
                                                                                            settings.farm_emoji)
        else:
            fl_desc = "{0}**Farm Upgrade**:\nYou already have the max level farm!".format(settings.farm_emoji)

        if not database.has_inventory(authorID, "binoculars"):
            bin_desc = "{2}**Binoculars**: {0} {1}\nFind1.5x as much eggs when hunting".format(settings.binocular_cost,
                                                                                               settings.eggy_emoji,
                                                                                               settings.binoculars_emoji)
        else:
            bin_desc = "{2}**Binoculars** (**owned**): {0} {1}\nFind 1.5x as much eggs when hunting".format(
                settings.binocular_cost, settings.silver_eggy_emoji, settings.binoculars_emoji)

        if not database.has_inventory(authorID, "lucky drumstick"):
            ld_desc = "{2}**Lucky Drumstick**: {1} {0}\nHigher chance to find silver eggs while chatting".format(
                settings.silver_eggy_emoji, settings.lucky_drumstick_cost, settings.drumstick_emoji)
        else:
            ld_desc = "{2}**Lucky Drumstick** (**owned**): {1} {0}\nHigher chance to find silver eggs while chatting".format(
                settings.silver_eggy_emoji, settings.lucky_drumstick_cost, settings.drumstick_emoji)

        if not database.has_inventory(authorID, "golden chicken"):
            gc_desc = "{2}**Golden Chicken**: {1} {0}\nincrease your harvest by 1.5x.".format(
                settings.silver_eggy_emoji,
                settings.golden_chicken_cost, settings.chicken_emoji)
        else:
            gc_desc = "{2}**Golden Chicken** (**owned**): {1} {0}\nincrease your harvest by 1.5x.".format(
                settings.silver_eggy_emoji, settings.golden_chicken_cost, settings.chicken_emoji)

        if not database.has_inventory(authorID, "eggcellent statue"):
            es_desc = "{2}**Eggcellent Statue**: {1} {0}\nA statue to signify your devotion to egg".format(
                settings.golden_eggy_emoji, settings.egg_statue_cost, settings.eggy_statue_emoji)
        else:
            count = 0
            for invobj in database.get_user(authorID).inventory:
                if invobj == "eggcellent statue":
                    count += 1
            es_desc = "{3}**Eggcellent Statue** (**{2} owned**): {1} {0}\nA statue to signify your devotion to egg".format(
                settings.golden_eggy_emoji, settings.egg_statue_cost, count, settings.eggy_statue_emoji)

        if not database.has_inventory(authorID, "delicate shovel"):
            ds_desc = "{2}**Delicate Shovel**: {1} {0}\nCan be used to dig out lost eggs from the soil".format(
                settings.eggy_emoji, settings.delicate_shovel_cost, settings.shovel_emoji)
        else:
            ds_desc = "{2}**Delicate Shovel** (**owned**): {1} {0}\nCan be used to dig out lost eggs from the soil".format(
                settings.eggy_emoji, settings.delicate_shovel_cost, settings.shovel_emoji)

        if not database.has_inventory(authorID, "egg topper"):
            et_desc = "{2}**Egg Topper**: {1} {0}\nCan be used to make an egg into egg yolk".format(
                settings.eggy_emoji, settings.egg_toper_cost, settings.topper_emoji)
        else:
            count = 0
            for invobj in database.get_user(authorID).inventory:
                if invobj == "egg topper":
                    count += 1
            et_desc = "{3}**Egg Topper** (**{2} owned**): {1} {0}\nCan be used to make an egg into egg yolk".format(
                settings.eggy_emoji, settings.egg_toper_cost, count, settings.topper_emoji)

        if not database.has_inventory(authorID, "golden shovel"):
            gs_desc = "{2}**Golden Shovel**: {1} {0}\nDoes the work of a shovel but 1.5x better!".format(
                settings.golden_eggy_emoji, settings.golden_shovel_cost, settings.golden_shovel_emoji)
        else:
            gs_desc = "{2}**Golden Shovel** (**owned**): {1} {0}\nDoes the work of a shovel but 1.5x better!".format(
                settings.golden_eggy_emoji, settings.golden_shovel_cost, settings.golden_shovel_emoji)

        # emb.add_field(name="more coming soon", value="probably...", inline=False)

        # emb.description = fl_desc + "\n" + bin_desc + "\n" + ld_desc + "\n" + gc_desc
        emb.description = fl_desc + "\n\n" + et_desc + "\n\n" + ds_desc + "\n\n" + gc_desc + "\n\n" + bin_desc + "\n\n" + ld_desc + "\n\n" + es_desc + "\n\n" + gs_desc

        emb.set_author(name="The Egg Market",
                       icon_url="https://cdn.discordapp.com/attachments/1122532250915975208/1123268970674401392/360_F_526917681_vsjPlB6iYUPQvRqTYoElv8fDErQy24Lp-removebg-preview.png")

        await ctx.channel.send(embed=emb)
    elif store == "server" or store == "serv" or store == "s":
        emb = discord.Embed(
            title=None,
        )

        if not database.has_inventory(authorID, "custom role"):
            cr_desc = "**Custom Role**: {1} {0}\nA custom role with a colour and name of your choice".format(
                settings.golden_eggy_emoji, settings.custom_role_cost)
        else:
            cr_desc = "**Custom Role** (**owned**): {1} {0}\nA custom role with a colour and name of your choice".format(
                settings.golden_eggy_emoji, settings.custom_role_cost)

        if not database.has_inventory(authorID, "custom channel"):
            cc_desc = "**Custom Channel**: {1} {0}\nA custom channel that you can invite your friends to".format(
                settings.golden_eggy_emoji, settings.custom_channel_cost)
        else:
            cc_desc = "**Custom Channel** (**owned**): {1} {0}\nA custom channel that you can invite your friends to".format(
                settings.golden_eggy_emoji, settings.custom_channel_cost)

        emb.set_author(name="The Server Market",
                       icon_url="https://cdn.discordapp.com/attachments/1122532250915975208/1123268970674401392/360_F_526917681_vsjPlB6iYUPQvRqTYoElv8fDErQy24Lp-removebg-preview.png")

        emb.description = cr_desc + "\n\n" + cc_desc

        await ctx.channel.send(embed=emb)
    else:
        emb = discord.Embed(
            title="Which store would you like to go to?",
            description="The Economy Store ```+shop economy```\nThe Server Store ```+shop server```"
        )
        await ctx.channel.send(embed=emb)


@bot.command("buy", aliases=["purchase"])
async def buy(ctx, *, item):
    await eggy_check(ctx, False)
    authorID = ctx.author.id
    if item == "farm" or item == "farm upgrade":
        newlevel = database.get_user(authorID).farm_level + 1
        cost = settings.level_2_unlock_cost
        if newlevel == 2:
            cost = settings.level_2_unlock_cost
        elif newlevel == 3:
            cost = settings.level_3_unlock_cost
        elif newlevel == 4:
            cost = settings.level_4_unlock_cost
        elif newlevel == 5:
            cost = settings.level_5_unlock_cost
        elif newlevel >= 6:
            await ctx.channel.send("you already have the max farm level!")
            return

        if database.get_user(authorID).cash >= cost:
            database.give_cash(authorID, -cost)
            database.give_level(authorID, 1)
            await ctx.channel.send(
                "successfully purchased the level {0} farm upgrade for {1} {2}".format(newlevel, cost,
                                                                                       settings.cash_name))
        else:
            await ctx.channel.send("you don't have enough eggs to purchase this")
    elif item == "binoculars":
        cost = settings.binocular_cost
        if database.get_user(authorID).ironcash >= cost:
            database.give_cash(authorID, -cost)
            database.give_inv_item(authorID, 1, "binoculars")
            await ctx.channel.send(
                "successfully purchased the binoculars for {2} {0} {1}".format(cost, settings.cash_name,
                                                                               settings.eggy_emoji))
        else:
            await ctx.channel.send("you don't have enough silver eggs to purchase this")
    elif item == "luckydrumstick" or item == "lucky drumstick" or item == "lucky_drumstick":
        cost = settings.lucky_drumstick_cost
        if database.get_user(authorID).ironcash >= cost:
            database.give_cash(authorID, -cost)
            database.give_inv_item(authorID, 1, "lucky drumstick")
            await ctx.channel.send(
                "successfully purchased the lucky drumstick for {2} {0} {1}".format(cost, settings.cash_name,
                                                                                    settings.silver_eggy_emoji))
        else:
            await ctx.channel.send("you don't have enough silver eggs to purchase this")
    elif item == "goldenchicken" or item == "golden chicken" or item == "gold chicken" or item == "golden_chicken" or item == "gold_chicken":
        cost = settings.golden_chicken_cost
        if database.get_user(authorID).ironcash >= cost:
            database.give_iron_cash(authorID, -cost)
            database.give_inv_item(authorID, 1, "golden chicken")
            await ctx.channel.send(
                "successfully purchased the golden chicken for {2} {0} {1}".format(cost, settings.iron_cash_name,
                                                                                   settings.silver_eggy_emoji))
        else:
            await ctx.channel.send("you don't have enough silver eggs to purchase this")
    elif item == "custom role" or item == "customrole" or item == "custom_role":
        cost = settings.custom_role_cost
        mchannel = bot.get_channel(settings.mailbox_channel_id)
        srole = bot.get_guild(settings.guild_id).get_role(settings.staff_role)
        if mchannel is None or srole is None:
            await ctx.channel.send("something went wrong! purchase cancelled!")
            return
        elif database.get_user(authorID).goldcash >= cost:
            database.give_gold_cash(authorID, -cost)
            database.give_inv_item(authorID, 1, "custom role")
            await ctx.channel.send(
                "successfully purchased the custom role for {2} {0} {1}. staff will contact you shortly to grant you your role".format(
                    cost, settings.gold_cash_name,
                    settings.golden_eggy_emoji))
            await mchannel.send("{1.mention}! {0.mention} bought custom role!".format(ctx.author, srole))
        else:
            await ctx.channel.send("you don't have enough golden eggs to purchase this")
    elif item == "custom channel" or item == "customchannel" or item == "custom channel":
        cost = settings.custom_channel_cost
        mchannel = bot.get_channel(settings.mailbox_channel_id)
        srole = bot.get_guild(settings.guild_id).get_role(settings.staff_role)
        if mchannel is None or srole is None:
            await ctx.channel.send("something went wrong! purchase cancelled!")
            return
        elif database.get_user(authorID).goldcash >= cost:
            database.give_gold_cash(authorID, -cost)
            database.give_inv_item(authorID, 1, "custom channel")
            await ctx.channel.send(
                "successfully purchased the custom channel for {2} {0} {1}. staff will contact you shortly to grant you your channel".format(
                    cost, settings.gold_cash_name,
                    settings.golden_eggy_emoji))
            await mchannel.send("{1.mention}! {0.mention} bought custom channel!".format(ctx.author, srole))
        else:
            await ctx.channel.send("you don't have enough golden eggs to purchase this")
    elif item == "egg statue" or item == "eggy statue" or item == "egg_statue" or item == "eggy_stateu" or item == "eggcellent statue" or item == "eggcellent_statue":
        cost = settings.egg_statue_cost
        if database.get_user(authorID).goldcash >= cost:
            database.give_iron_cash(authorID, -cost)
            database.give_inv_item(authorID, 1, "eggcellent statue")
            await ctx.channel.send(
                "successfully purchased a eggcellent statue for {2} {0} {1}".format(cost, settings.gold_cash_name,
                                                                                    settings.golden_eggy_emoji))
        else:
            await ctx.channel.send("you don't have enough golden eggs to purchase this")
    elif item == "egg topper" or item == "eggy topper" or item == "egg_topper" or item == "eggy_topper":
        cost = settings.egg_toper_cost
        if database.get_user(authorID).cash >= cost:
            database.give_cash(authorID, -cost)
            database.give_inv_item(authorID, 1, "egg topper")
            await ctx.channel.send(
                "successfully purchased the egg topper for {2} {0} {1}".format(cost, settings.cash_name,
                                                                               settings.eggy_emoji))
        else:
            await ctx.channel.send("you don't have enough eggs to purchase this")
    elif item == "shovel" or item == "delicate shovel" or item == "delicate_shovel":
        cost = settings.delicate_shovel_cost
        if database.get_user(authorID).cash >= cost:
            database.give_iron_cash(authorID, -cost)
            database.give_inv_item(authorID, 1, "delicate shovel")
            await ctx.channel.send(
                "successfully purchased the delicate shovel for {2} {0} {1}".format(cost, settings.cash_name,
                                                                                    settings.golden_eggy_emoji))
        else:
            await ctx.channel.send("you don't have enough eggs to purchase this")
    else:
        await ctx.channel.send("invalid item")


@buy.error
async def buy_error(ctx, error):
    await error_handling(ctx, error, "buy")


@bot.command("pay", aliases=["give"])
@commands.has_role(842686615092199444)
async def pay(ctx, target: discord.Member, amount: int, what):
    targetID = target.id
    if what == "egg" or what == "eggs":
        database.give_cash(targetID, amount)
        emb = discord.Embed(
            title="success",
            description="successfully payed {3} {0} {1} to {2}".format(amount, settings.cash_name, target,
                                                                       settings.eggy_emoji)
        )

        emb.set_author(name="Egg Basket",
                       icon_url="https://cdn.discordapp.com/attachments/1121483496435753100/1121876394905981069/download__2_-removebg-preview.png")
        emb.set_footer(text=str(date.today()))

        await ctx.channel.send(embed=emb)
    elif what == "segg" or what == "silveregg" or what == "silvereggs":
        database.give_iron_cash(targetID, amount)
        emb = discord.Embed(
            title="success",
            description="successfully payed {3} {0} {1} to {2}".format(amount, settings.iron_cash_name, target,
                                                                       settings.silver_eggy_emoji)
        )

        emb.set_author(name="Egg Basket",
                       icon_url="https://cdn.discordapp.com/attachments/1121483496435753100/1121876394905981069/download__2_-removebg-preview.png")
        emb.set_footer(text=str(date.today()))

        await ctx.channel.send(embed=emb)
    elif what == "gegg" or what == "goldegg" or what == "goldeggs" or what == "goldenegg" or what == "goldeneggs":
        database.give_gold_cash(targetID, amount)
        emb = discord.Embed(
            title="success",
            description="successfully payed {3} {0} {1} to {2}".format(amount, settings.gold_cash_name, target,
                                                                       settings.golden_eggy_emoji)
        )

        emb.set_author(name="Egg Basket",
                       icon_url="https://cdn.discordapp.com/attachments/1121483496435753100/1121876394905981069/download__2_-removebg-preview.png")
        emb.set_footer(text=str(date.today()))

        await ctx.channel.send(embed=emb)
    elif what == "eggyolk" or what == "eggyolks" or what == "yolk" or what == "yolks":
        database.give_yolk_cash(targetID, amount)
        emb = discord.Embed(
            title="success",
            description="successfully payed {3} {0} {1} to {2}".format(amount, settings.yolk_cash_name, target,
                                                                       settings.eggyolk_emoji)
        )

        emb.set_author(name="Egg Basket",
                       icon_url="https://cdn.discordapp.com/attachments/1121483496435753100/1121876394905981069/download__2_-removebg-preview.png")
        emb.set_footer(text=str(date.today()))
    elif what == "test":
        database.give_inv_item(targetID, amount, settings.test_object_name)
        emb = discord.Embed(
            title="success",
            description="successfully gave {0} {1}s to {2}".format(amount, settings.test_object_name, target)
        )

        emb.set_author(name="Egg Basket",
                       icon_url="https://cdn.discordapp.com/attachments/1121483496435753100/1121876394905981069/download__2_-removebg-preview.png")
        emb.set_footer(text=str(date.today()))
        await ctx.channel.send(embed=emb)
    else:
        await ctx.channel.send("there is no object with that name")


@pay.error
async def pay_error(ctx, error):
    await error_handling(ctx, error, "pay")


@bot.command("inventory", aliases=["inv", "wares"])
async def inventory(ctx):
    authorID = ctx.author.id
    u = database.get_user(authorID)
    if len(u.inventory) == 0:
        emb = discord.Embed(
            title="{0}'s warehouse".format(ctx.author.name),
            description="your inventory is currently empty!"
        )

        await ctx.channel.send(embed=emb)
    else:
        emb = discord.Embed(
            title="{0}'s warehouse".format(ctx.author.name)
        )
        test = 0  # done
        statue = 0  # not done
        egg_topper = 0
        custom_role = 0  # done
        custom_channel = 0  # done
        for invobj in u.inventory:
            if invobj == "test":
                test += 1
            elif invobj == "eggcellent statue":
                statue += 1
            elif invobj == "egg topper":
                egg_topper += 1
            elif invobj == "custom role":
                custom_role += 1
            elif invobj == "custom channel":
                custom_channel += 1

        if database.has_inventory(authorID, "dev crown"):
            emb.add_field(name=":crown: Dev Crown", value="A crown only the developer can give", inline=True)
        if test != 0:
            emb.add_field(name="Test", value="You have {0} {1}s".format(test, settings.test_object_name), inline=True)
        if database.has_inventory(authorID, "binoculars"):
            emb.add_field(name="Binoculars", value="You have the binoculars", inline=True)
        if database.has_inventory(authorID, "lucky drumstick"):
            emb.add_field(name="Lucky Drumstick", value="You have the lucky drumstick", inline=True)
        if database.has_inventory(authorID, "golden chicken"):
            emb.add_field(name="Golden Chicken", value="You have the golden chicken")
        if egg_topper == 1:
            emb.add_field(name="Egg Topper", value="You have a egg topper")
        elif egg_topper >= 2:
            emb.add_field(name="Egg Topper", value="You have {0} egg toppers".format(egg_topper))
        if database.has_inventory(authorID, "delicate shovel"):
            emb.add_field(name="Delicate Shovel", value="You have the delicate shovel")
        if database.has_inventory(authorID, "golden shovel"):
            emb.add_field(name="Golden Shovel", value="You have the golden shovel")
        if statue == 1:
            emb.add_field(name="Eggcellent Statue", value="You have a eggcellent statue")
        elif statue >= 2:
            emb.add_field(name="Eggcellent Statue", value="You have {0} eggcellent statues".format(statue))

        await ctx.channel.send(embed=emb)


@bot.command("profile", aliases=["prof"])
async def profile(ctx):
    await eggy_check(ctx, False)
    authorID = ctx.author.id
    emb = discord.Embed(
        title=""
    )

    emb.add_field(name="{0}Farm Level".format(settings.farm_emoji),
                  value="You are currently farm level {0}".format(database.get_user(ctx.author.id).farm_level),
                  inline=False)

    u = database.get_user(authorID)
    emb.add_field(name="Basket",
                  value="You currently have:" + "\n" +
                        "{2} {0} {1}".format(u.cash, settings.cash_name, settings.eggy_emoji) + "\n" +
                        "{2} {0} {1}".format(u.ironcash, settings.iron_cash_name, settings.silver_eggy_emoji) + "\n" +
                        "{2} {0} {1}".format(u.goldcash, settings.gold_cash_name, settings.golden_eggy_emoji) + "\n" +
                        "{2} {0} {1}".format(u.eggyolks, settings.yolk_cash_name, settings.eggyolk_emoji),
                  inline=False)

    emb.set_author(name="{0}'s profile".format(ctx.author.name), url=None, icon_url=ctx.author.avatar)

    await ctx.channel.send(embed=emb)


@bot.command("nick", aliases=["yoink", "take"])
@commands.has_role(settings.staff_role)
async def nick(ctx, target: discord.Member, amount: int, what):
    targetID = target.id
    amount = -amount
    if what == "egg" or what == "eggs":
        database.give_cash(targetID, amount)
        emb = discord.Embed(
            title="success",
            description="successfully nicked {3} {0} {1} from {2}".format(amount, settings.cash_name, target,
                                                                          settings.eggy_emoji)
        )

        emb.set_author(name="Egg Basket",
                       icon_url="https://cdn.discordapp.com/attachments/1121483496435753100/1121876394905981069/download__2_-removebg-preview.png")
        emb.set_footer(text=str(date.today()))

        await ctx.channel.send(embed=emb)
    elif what == "segg" or what == "silveregg" or what == "silvereggs":
        database.give_iron_cash(targetID, amount)
        emb = discord.Embed(
            title="success",
            description="successfully nicked {3} {0} {1} from {2}".format(amount, settings.iron_cash_name, target,
                                                                          settings.silver_eggy_emoji)
        )

        emb.set_author(name="Egg Basket",
                       icon_url="https://cdn.discordapp.com/attachments/1121483496435753100/1121876394905981069/download__2_-removebg-preview.png")
        emb.set_footer(text=str(date.today()))

        await ctx.channel.send(embed=emb)
    elif what == "gegg" or what == "goldegg" or what == "goldeggs" or what == "goldenegg" or what == "goldeneggs":
        database.give_gold_cash(targetID, amount)
        emb = discord.Embed(
            title="success",
            description="successfully nicked {3} {0} {1} from {2}".format(amount, settings.gold_cash_name, target,
                                                                          settings.golden_eggy_emoji)
        )

        emb.set_author(name="Egg Basket",
                       icon_url="https://cdn.discordapp.com/attachments/1121483496435753100/1121876394905981069/download__2_-removebg-preview.png")
        emb.set_footer(text=str(date.today()))

        await ctx.channel.send(embed=emb)
    elif what == "eggyolk" or what == "eggyolks" or what == "yolk" or what == "yolks":
        database.give_yolk_cash(targetID, amount)
        emb = discord.Embed(
            title="success",
            description="successfully nicked {3} {0} {1} from {2}".format(amount, settings.yolk_cash_name, target,
                                                                          settings.eggyolk_emoji)
        )

        emb.set_author(name="Egg Basket",
                       icon_url="https://cdn.discordapp.com/attachments/1121483496435753100/1121876394905981069/download__2_-removebg-preview.png")
        emb.set_footer(text=str(date.today()))
    else:
        await ctx.channel.send("there is no object with that name")


@nick.error
async def nick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.channel.send("you do not have permission to do this!")
    elif isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.ConversionError):
        await ctx.channel.send("invalid arguments! {0}nick (target) (amount)".format(settings.bot_prefix))


@bot.command("hunt", aliases=["search"])
@commands.cooldown(1, settings.hunt_cooldown, commands.BucketType.user)
async def hunt(ctx):
    await eggy_check(ctx, False)
    rolled = random.randint(1, 100)
    if rolled <= settings.hunt_chance:
        rolled_place = settings.hunt_locations[random.randint(0, (len(settings.hunt_locations) - 1))]
        rolled_eggs = 0
        flevel = database.get_user(ctx.author.id).farm_level
        if flevel == 1:
            rolled_eggs = random.randint(settings.level_1_farm_min, settings.level_1_farm_max)
        elif flevel == 2:
            rolled_eggs = random.randint(settings.level_2_farm_min, settings.level_2_farm_max)
        elif flevel == 3:
            rolled_eggs = random.randint(settings.level_3_farm_min, settings.level_3_farm_max)
        elif flevel == 4:
            rolled_eggs = random.randint(settings.level_4_farm_min, settings.level_4_farm_max)
        elif flevel == 5:
            rolled_eggs = random.randint(settings.level_5_farm_min, settings.level_5_farm_max)

        if database.has_inventory(ctx.author.id, "binoculars"):
            rolled_eggs = rolled_eggs * 2

        database.give_cash(ctx.author.id, rolled_eggs)

        emb = discord.Embed(
            title="Found some {0}".format(settings.cash_name),
            description="You found {0} {3} {1} {2}".format(rolled_eggs, settings.cash_name, rolled_place,
                                                           settings.eggy_emoji)
        )

        await ctx.send(embed=emb)
    else:
        await ctx.channel.send("you didn't find any eggs")


@hunt.error
async def hunt_error(ctx, error):
    await error_handling(ctx, error, "hunt")


@bot.command("dupe", aliases=["duplicate"])
async def dupe(ctx, amount):
    await eggy_check(ctx, False)
    if amount == "all" or amount == "max":
        amount = database.get_user(ctx.author.id).cash
    else:
        try:
            amount = int(amount)
        except ValueError:
            await ctx.channel.send("invalid arguments! {0}dupe (amount)".format(settings.bot_prefix))
            return
    if amount > 50:
        await ctx.channel.send("you cant duplicate so many eggs theres a max of 50")
        return
    authorID = ctx.author.id
    amount = int(amount)
    if not database.get_user(authorID).cash >= amount:
        await ctx.channel.send("you dont have enough eggs")
        return
    rolled = random.randint(1, 100)
    if rolled <= settings.dupe_chance:
        database.give_cash(authorID, amount)
        await ctx.channel.send("you successfully duplicated {0} {1}".format(amount, settings.cash_name))
    else:
        database.give_cash(authorID, -amount)
        await ctx.channel.send("oops you dropped the eggs on your way to the machine")


@bot.command("crack")
async def crack(ctx):
    authorID = ctx.author.id
    if database.has_inventory(authorID, "egg topper"):
        rolled = random.randint(1, 100)
        if rolled <= 50:
            rolled = random.randint(1, 100)
            if rolled <= 25:
                database.give_yolk_cash(authorID, 2)
                await ctx.channel.send("you found 2 egg yolks inside the egg but the egg topper broke")
            else:
                database.give_yolk_cash(authorID, 1)
                await ctx.channel.send("you found 1 egg yolk inside the egg but the egg topper broke")
        else:
            await ctx.channel.send("you broke the egg and the egg topper")
        database.remove_inv_item(authorID, 1, "egg topper")
        database.give_cash(authorID, -1)
    else:
        await ctx.channel.send("you need the egg topper to use this command!")


@bot.command("dig")
@commands.cooldown(1, settings.dig_cooldown, commands.BucketType.user)
async def dig(ctx):
    authorID = ctx.author.id
    if database.has_inventory(authorID, "delicate shovel") or database.has_inventory(authorID, "golden shovel"):
        flevel = database.get_user(authorID).farm_level
        if flevel == 1:
            rolled = random.randint(settings.level_1_farm_min - 1, settings.level_1_farm_max - 1)
        elif flevel == 2:
            rolled = random.randint(settings.level_2_farm_min - 1, settings.level_2_farm_max - 1)
        elif flevel == 3:
            rolled = random.randint(settings.level_3_farm_min - 1, settings.level_3_farm_max - 1)
        elif flevel == 4:
            rolled = random.randint(settings.level_4_farm_min - 1, settings.level_4_farm_max - 1)
        elif flevel == 5:
            rolled = random.randint(settings.level_5_farm_min - 1, settings.level_5_farm_max - 1)

        if rolled <= 0:
            await ctx.channel.send("you broke the eggs while digging them up")
            return

        if database.has_inventory(authorID, "golden shovel"):
            rolled = round(rolled * 1.5)

        database.give_cash(authorID, rolled)
        await ctx.channel.send("you dug up {0} eggs".format(rolled))
    else:
        await ctx.channel.send("you dont own a shovel")


async def error_handling(ctx, error, command):
    if isinstance(error, commands.MissingPermissions) or isinstance(error, commands.MissingRole):
        await ctx.channel.send("https://tenor.com/view/no-nope-non-rick-rick-and-morty-gif-20999440")
    elif isinstance(error, commands.MissingRequiredArgument):
        if command == "announce":
            await ctx.channel.send(
                "missing required argument! {0}announce (title)|(announcement)|(?banner). yes the '|' is neccesary".format(
                    settings.bot_prefix))
        elif command == "transfer":
            await ctx.channel.send("missing required argument! {0}share (target) (amount)".format(settings.bot_prefix))
        elif command == "buy":
            await ctx.channel.send("missing required argument! {0}buy (item)".format(settings.bot_prefix))
        elif command == "pay":
            await ctx.channel.send("missing required argument! {0}pay (target) (amoun)".format(settings.bot_prefix))
    elif isinstance(error, commands.ConversionError):
        if command == "transfer":
            await ctx.channel.send("invalid arguments! {0}share (target) (amount)".format(settings.bot_prefix))
        elif command == "pay":
            await ctx.channel.send("invalid arguments! {0}pay (target) (amount)".format(settings.bot_prefix))
        elif command == "dupe":
            await ctx.channel.send("invalid arguments! {0}dupe (amount)".format(settings.bot_prefix))
    elif isinstance(error, commands.CommandOnCooldown):
        if command == "harvest":
            await ctx.channel.send(
                f"The eggs arent ready to harvest. you should check again in {error.retry_after:.0f} seconds.")
        elif command == "hunt":
            await ctx.channel.send(
                f"you just went searching you should get some rest and go again in {error.retry_after:.0f} seconds.")
        elif command == "dupe":
            await ctx.channel.send(
                f"the machine is still charging it should be done in {error.retry_after:.0f} seconds.")
        elif command == "dig":
            await ctx.channel.send(f"you are still resting you can go again in {error.retry_after:.0f} seconds.")


async def eggy_check(ctx, chatted: bool):
    authorID = ctx.author.id
    if database.get_user(authorID).farm_level >= 4:
        has_a_chance = (random.randint(1, 4) == 1)
        if has_a_chance:
            silver = (random.randint(1, 2) == 1)
            rolled = random.randint(1, 100)
            if database.has_inventory(authorID, "lucky drumstick"):
                rolled *= 1.5
                if rolled > 100:
                    rolled = 100
            if silver:
                if database.get_user(authorID).farm_level == 4:
                    if rolled <= settings.level_4_silver_chance:
                        database.give_iron_cash(authorID, 1)
                        await ctx.channel.send(
                            "you found a {1} {0}!".format(settings.iron_cash_name, settings.silver_eggy_emoji))
                elif database.get_user(authorID).farm_level == 5:
                    if rolled <= settings.level_5_silver_chance:
                        database.give_iron_cash(authorID, 1)
                        await ctx.channel.send(
                            "you found a {1} {0}!".format(settings.iron_cash_name, settings.silver_eggy_emoji))
            elif not chatted:
                if database.get_user(authorID).farm_level == 4:
                    if rolled <= settings.level_4_gold_chance:
                        database.give_gold_cash(authorID, 1)
                        await ctx.channel.send(
                            "you found a {1} {0}!".format(settings.gold_cash_name, settings.golden_eggy_emoji))
                elif database.get_user(authorID).farm_level == 5:
                    if rolled <= settings.level_5_gold_chance:
                        database.give_gold_cash(authorID, 1)
                        await ctx.channel.send(
                            "you found a {1} {0}!".format(settings.gold_cash_name, settings.golden_eggy_emoji))


@bot.command("test_emojis")
@commands.has_role(863434428570796043)
async def test_emojis(ctx):
    await ctx.channel.send(settings.farm_emoji
                           + "," + settings.eggy_emoji
                           + "," + settings.eggyolk_emoji
                           + "," + settings.golden_eggy_emoji
                           + "," + settings.silver_eggy_emoji
                           + "," + settings.binoculars_emoji
                           + "," + settings.chicken_emoji
                           + "," + settings.drumstick_emoji
                           + "," + settings.shovel_emoji
                           + "," + settings.topper_emoji
                           )
    time.sleep(2.5)
    await ctx.channel.purge(limit=2)


@test_emojis.error
async def test_emojis_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.channel.send("https://tenor.com/view/no-nope-non-rick-rick-and-morty-gif-20999440")


# keep_alive()  # Starts a webserver to be pinged.
token = ""

bot.run(token)  # Starts the bot
