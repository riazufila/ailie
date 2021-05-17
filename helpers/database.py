#!/usr/bin/env python

from datetime import datetime
import pytz
import time
import math
import os
import psycopg2


class Database():
    def __init__(self):
        DATABASE_URL = os.environ["DATABASE_URL"]
        self.connection = psycopg2.connect(DATABASE_URL, sslmode="require")
        self.cursor = self.connection.cursor()

    def initialize_user(self, guardian_id):
        initialized = False

        query = "SELECT guardian_id FROM guardians WHERE guardian_id = %s;"
        data = [guardian_id]
        self.cursor.execute(query, data)
        row = self.cursor.fetchone()
        if row:
            initialized = True
        else:
            initialized = False

        if not initialized:
            query = "INSERT INTO guardians (guardian_id) VALUES (%s);"
            data = [guardian_id]
            self.cursor.execute(query, data)

            query = "INSERT INTO inventories (guardian_id) VALUES (%s);"
            data = [guardian_id]
            self.cursor.execute(query, data)

            self.connection.commit()

            return True
        else:
            return False

    def is_initialized(self, guardian_id):
        query = "SELECT guardian_id FROM guardians WHERE guardian_id = %s;"
        data = [guardian_id]
        self.cursor.execute(query, data)
        initialize_check = self.cursor.fetchone()

        if initialize_check:
            return True
        else:
            return False

    def get_all_guardians_id(self):
        query = "SELECT guardian_id FROM guardians;"
        self.cursor.execute(query)
        all_guardians = self.cursor.fetchall()

        buffer = []
        if all_guardians:
            for guardian in all_guardians:
                buffer.append(guardian[0])
            return buffer
        else:
            return []

    def get_username(self, guardian_id):
        query = (
            "SELECT guardian_username FROM guardians "
            + "WHERE guardian_id = %s;"
        )
        data = [guardian_id]
        self.cursor.execute(query, data)
        guardian_username = self.cursor.fetchone()

        if isinstance(guardian_username, tuple):
            guardian_username = guardian_username[0]

        if guardian_username:
            return guardian_username
        else:
            return None

    def get_guardian_info(self, guardian_id):
        query = (
            "SELECT guardian_username, guild_id, guardian_gems FROM guardians "
            + "WHERE guardian_id = %s;"
        )
        data = [guardian_id]
        self.cursor.execute(query, data)
        row = self.cursor.fetchone()
        guild_username = row[0]
        gems = row[2]

        if row[1]:
            query = (
                "SELECT guild_name, guardian_position FROM guardians "
                + "INNER JOIN guilds ON guardians.guild_id = "
                + "guilds.guild_id WHERE guardian_id = %s;"
            )
            data = [guardian_id]
            self.cursor.execute(query, data)
            row = self.cursor.fetchone()

            guild_name = row[0]
            guardian_position = row[1]
        else:
            guild_name = None
            guardian_position = None

        return guild_username, guild_name, guardian_position, gems

    def set_username(self, guardian_id, guardian_username):
        query = (
            "UPDATE guardians SET guardian_username = %s "
            + "WHERE guardian_id = %s;"
        )
        data = [guardian_username, guardian_id]
        self.cursor.execute(query, data)
        self.connection.commit()

    def create_guild(
        self, guardian_id, guardian_position, guild_id, guild_name
    ):
        query = "INSERT INTO guilds (guild_id, guild_name) VALUES (%s, %s);"
        data = [guild_id, guild_name]
        self.cursor.execute(query, data)
        self.connection.commit()
        self.join_guild(guardian_id, guardian_position, guild_id)

    def join_guild(self, guardian_id, guardian_position, guild_id):
        query = (
            "UPDATE guardians SET guild_id = %s, "
            + "guardian_position = %s WHERE guardian_id = %s;"
        )
        data = (guild_id, guardian_position, guardian_id)
        self.cursor.execute(query, data)
        self.connection.commit()

    def is_guildless(self, guardian_id):
        query = "SELECT guild_id FROM guardians WHERE guardian_id = %s;"
        data = [guardian_id]
        self.cursor.execute(query, data)

        row = self.cursor.fetchone()

        if isinstance(row, tuple):
            row = row[0]

        if row:
            return False
        else:
            return True

    def guild_exists(self, guild_id):
        query = "SELECT guild_id FROM guilds WHERE guild_id = %s;"
        data = [guild_id]
        self.cursor.execute(query, data)

        row = self.cursor.fetchone()

        if isinstance(row, tuple):
            row = row[0]

        if row:
            return True
        else:
            return False

    def get_guild_name(self, guild_id):
        query = "SELECT guild_name FROM guilds WHERE guild_id = %s;"
        data = [guild_id]
        self.cursor.execute(query, data)

        row = self.cursor.fetchone()

        if isinstance(row, tuple):
            row = row[0]

        # Return Guild Name
        return row

    def get_guild_master(self, guild_id):
        query = (
            "SELECT guardian_id FROM guardians WHERE "
            + "guild_id = %s and guardian_position = %s;"
        )
        data = [guild_id, "Guild Master"]
        self.cursor.execute(query, data)

        row = self.cursor.fetchone()

        if isinstance(row, tuple):
            row = row[0]

        if row:
            return row
        else:
            return row

    def get_members_list(self, guardian_id):
        query = "SELECT guild_id FROM guardians WHERE guardian_id = %s;"
        data = [guardian_id]
        self.cursor.execute(query, data)

        row = self.cursor.fetchone()

        if isinstance(row, tuple):
            row = row[0]

        guild_id = row

        query = (
            "SELECT guardian_id, guardian_username, guardian_position "
            + "FROM guardians WHERE guild_id = %s;"
        )
        data = [guild_id]
        self.cursor.execute(query, data)
        members = self.cursor.fetchall()

        return members

    def get_guild_name_of_member(self, guardian_id):
        query = (
            "SELECT guild_name FROM guilds INNER JOIN guardians "
            + "ON guilds.guild_id = guardians.guild_id "
            + "WHERE guardians.guardian_id = %s;"
        )
        data = [guardian_id]
        self.cursor.execute(query, data)
        row = self.cursor.fetchone()

        if isinstance(row, tuple):
            row = row[0]

        guild_name = row

        return guild_name

    def change_position(self, guardian_id, position):
        query = (
            "UPDATE guardians SET guardian_position = %s "
            + "WHERE guardian_id = %s;"
        )
        data = [position, guardian_id]
        self.cursor.execute(query, data)
        self.connection.commit()

    def get_guild_id_of_member(self, guardian_id):
        query = "SELECT guild_id FROM guardians WHERE guardian_id = %s;"
        data = [guardian_id]
        self.cursor.execute(query, data)
        row = self.cursor.fetchone()

        if isinstance(row, tuple):
            row = row[0]

        guild_id = row

        return guild_id

    def total_members(self, guild_id):
        query = "SELECT guardian_id FROM guardians WHERE guild_id = %s;"
        data = [guild_id]
        self.cursor.execute(query, data)

        row = self.cursor.fetchall()

        return len(row)

    def disband_guild(self, guild_id):
        query = (
            "UPDATE guardians SET guardian_position = NULL, "
            + "guild_id = NULL WHERE guild_id = %s;"
        )
        data = [guild_id]
        self.cursor.execute(query, data)

        query = "DELETE FROM guilds WHERE guild_id = %s;"
        data = [guild_id]
        self.cursor.execute(query, data)

        self.connection.commit()

    def quit_guild(self, guardian_id):
        query = "UPDATE guardians SET guild_id = NULL WHERE guardian_id = %s;"
        data = [guardian_id]
        self.cursor.execute(query, data)
        self.connection.commit()

    def store_gems(self, guardian_id, gems):
        # Get already existing gems
        query = "SELECT guardian_gems FROM guardians WHERE guardian_id = %s;"
        data = [guardian_id]
        self.cursor.execute(query, data)

        old_gems = self.cursor.fetchone()

        if isinstance(old_gems, tuple):
            old_gems = old_gems[0]

        # Add total gems
        new_gems = old_gems + gems

        # Update into database
        query = (
            "UPDATE guardians SET guardian_gems = %s WHERE guardian_id = %s;"
        )
        data = [new_gems, guardian_id]
        self.cursor.execute(query, data)
        self.connection.commit()

    def get_gems(self, guardian_id):
        # Get already existing gems
        query = "SELECT guardian_gems FROM guardians WHERE guardian_id = %s;"
        data = [guardian_id]
        self.cursor.execute(query, data)

        row = self.cursor.fetchone()

        if isinstance(row, tuple):
            row = row[0]

        return row

    def spend_gems(self, guardian_id, gems):
        # Get current gems and substract with to be expended gems
        current_gems = self.get_gems(guardian_id)
        balance_gems = current_gems - gems

        if balance_gems < 0:
            return False
        else:
            # Query to update gems amount
            query = (
                "UPDATE guardians SET guardian_gems = %s "
                + "WHERE guardian_id = %s;"
            )
            data = [balance_gems, guardian_id]
            self.cursor.execute(query, data)
            self.connection.commit()

            return True

    def get_pool(self, type, pickup, stars):
        pool = stars[:]

        if pickup == "normal" and type == "heroes":
            query = "SELECT hero_star, hero_name FROM heroes;"
        elif pickup == "normal" and type == "equipments":
            query = (
                "SELECT equip_star, equip_name, equip_exclusive "
                + "FROM equipments;"
            )
        elif pickup == "pickup" and type == "heroes":
            query = (
                "SELECT hero_star, hero_name FROM heroes "
                + "WHERE hero_pickup = TRUE;"
            )
        else:
            query = (
                "SELECT equip_star, equip_name, equip_exclusive FROM "
                + "equipments WHERE equip_pickup = TRUE;"
            )

        self.cursor.execute(query)
        records = self.cursor.fetchall()

        for record in records:
            counter = 0
            star = record[0]
            name = record[1]

            while counter != star:
                if counter == 0:
                    if type == "equipments":
                        if record[2] is True:
                            name = "★ [Ex] " + name
                        else:
                            name = "★ " + name
                    else:
                        name = "★ " + name
                else:
                    name = "★" + name

                counter += 1

            if type == "heroes" and pickup == "normal":
                pool[star - 1].append(name)
            elif type == "equipments" and pickup == "normal":
                if record[2] is True:
                    pool[4].append(name)
                else:
                    pool[star - 2].append(name)
            else:
                pool.append(name)

        return pool

    def is_hero_obtained(self, guardian_id, hero_id):
        query = (
            "SELECT he.hero_id "
            + "FROM inventories i "
            + "INNER JOIN heroes_acquired h "
            + "ON i.inventory_id = h.inventory_id "
            + "INNER JOIN heroes he "
            + "ON h.hero_id = he.hero_id "
            + "WHERE i.guardian_id = %s AND he.hero_id = %s;"
        )
        data = [guardian_id, hero_id]
        self.cursor.execute(query, data)
        hero_obtained = self.cursor.fetchone()

        if hero_obtained:
            return True
        else:
            return False

    def is_equip_obtained(self, guardian_id, equip_id):
        query = (
            "SELECT eq.equip_id "
            + "FROM inventories i "
            + "INNER JOIN equipments_acquired ea "
            + "ON i.inventory_id = ea.inventory_id "
            + "INNER JOIN equipments eq "
            + "ON ea.equip_id = eq.equip_id "
            + "WHERE i.guardian_id = %s AND eq.equip_id = %s;"
        )
        data = [guardian_id, equip_id]
        self.cursor.execute(query, data)
        equip_obtained = self.cursor.fetchone()

        if equip_obtained:
            return True
        else:
            return False

    def hero_inventory(self, guardian_id):
        query = (
            "SELECT h.hero_star, h.hero_name, h.hero_id "
            + "FROM guardians g "
            + "INNER JOIN inventories i ON g.guardian_id = i.guardian_id "
            + "INNER JOIN heroes_acquired ha "
            + "ON i.inventory_id = ha.inventory_id "
            + "INNER JOIN heroes h ON ha.hero_id = h.hero_id "
            + "WHERE g.guardian_id = %s ORDER BY h.hero_star DESC;"
        )
        data = [guardian_id]
        self.cursor.execute(query, data)
        hero_inventory = self.cursor.fetchall()
        hero_buffer = [[], [], []]

        inventory_id = self.get_inventory_id(guardian_id)

        hero_with_level = []
        for hero in hero_inventory:
            acquired = self.get_hero_acquired_details(inventory_id, hero[2])
            ewp_id = self.get_exclusive_weapon_id(hero[2])
            obtained = self.is_equip_obtained(guardian_id, ewp_id)
            hero_with_level.append(
                [acquired["level"], hero[0], hero[1], hero[2], obtained])

        hero_inventory = sorted(hero_with_level, reverse=True)
        for hero in hero_inventory:
            if hero[0] == 0:
                hero[0] = "Z"

            if hero[4]:
                ewp_ind = " 🗡️"
            else:
                ewp_ind = ""

            if hero[1] == 3:
                hero_buffer[2].append(f"Lvl {hero[0]} ★★★ {hero[2]}{ewp_ind}")
            if hero[1] == 2:
                hero_buffer[1].append("Lvl {hero[0]} ★★ {hero[2]}{ewp_ind}")
            if hero[1] == 1:
                hero_buffer[0].append("Lvl {hero[0]} ★ {hero[2]}{ewp_ind}")

        return hero_buffer

    def item_inventory(self, guardian_id):
        query = (
            "SELECT it.item_name, ita.item_acquired_quantity "
            + "FROM guardians gu "
            + "INNER JOIN inventories i "
            + "ON gu.guardian_id = i.guardian_id "
            + "INNER JOIN items_acquired ita "
            + "ON i.inventory_id = ita.inventory_id "
            + "INNER JOIN items it "
            + "ON ita.item_id = it.item_id "
            + "WHERE gu.guardian_id = %s ORDER BY it.item_name;"
        )
        data = [guardian_id]
        self.cursor.execute(query, data)
        all_items = self.cursor.fetchall()

        buffer = [[]]
        for item in all_items:
            buffer[0].append(f"**{item[0]}** - `{item[1]:,d}`")

        return buffer

    def equip_inventory(self, guardian_id):
        query = (
            "SELECT eq.equip_star, eq.equip_exclusive, "
            + "eq.equip_name, eq.equip_id "
            + "FROM guardians g "
            + "INNER JOIN inventories i ON g.guardian_id = i.guardian_id "
            + "INNER JOIN equipments_acquired ea "
            + "ON i.inventory_id = ea.inventory_id "
            + "INNER JOIN equipments eq ON ea.equip_id = eq.equip_id "
            + "WHERE g.guardian_id = %s ORDER BY eq.equip_star DESC;"
        )
        data = [guardian_id]
        self.cursor.execute(query, data)
        equip_inventory = self.cursor.fetchall()
        equip_buffer = [[], [], [], [], [], []]

        inventory_id = self.get_inventory_id(guardian_id)

        equip_with_level = []
        for equip in equip_inventory:
            acquired = self.get_equip_acquired_details(inventory_id, equip[3])
            hero_id = self.get_hero_id_for_exclusive_weapon(equip[3])
            obtained = self.is_hero_obtained(guardian_id, hero_id)
            equip_with_level.append(
                [acquired["level"], equip[0], equip[1],
                    equip[2], equip[3], obtained]
            )

        equip_inventory = sorted(equip_with_level, reverse=True)
        for equip in equip_inventory:
            if equip[0] == 0:
                equip[0] = "Z"

            if equip[5]:
                hero_ind = " 👊"
            else:
                hero_ind = ""

            if equip[2]:
                if equip[1] == 5:
                    equip_buffer[5].append(
                        f"Lvl {equip[0]} ★★★★★ [Ex] {equip[3]}{hero_ind}")
                if equip[1] == 4:
                    equip_buffer[4].append(
                        f"Lvl {equip[0]} ★★★★ [Ex] {equip[3]}{hero_ind}")
            else:
                if equip[1] == 5:
                    equip_buffer[3].append(
                        f"Lvl {equip[0]} ★★★★★  {equip[3]}{hero_ind}")
                if equip[1] == 4:
                    equip_buffer[2].append(
                        f"Lvl {equip[0]} ★★★★ {equip[3]}{hero_ind}")
                if equip[1] == 3:
                    equip_buffer[1].append(
                        f"Lvl {equip[0]} ★★★ {equip[3]}{hero_ind}")
                if equip[1] == 2:
                    equip_buffer[0].append(
                        f"Lvl {equip[0]} ★★ {equip[3]}{hero_ind}")

        return equip_buffer

    def get_hero_id(self, name):
        # Get hero_id from heroes table
        query = "SELECT hero_id FROM heroes WHERE hero_name = %s;"
        data = [name]
        self.cursor.execute(query, data)

        hero_id = self.cursor.fetchone()

        if isinstance(hero_id, tuple):
            hero_id = hero_id[0]

        return hero_id

    def get_equip_id(self, name):
        # Get hero_id from heroes table
        query = "SELECT equip_id FROM equipments WHERE equip_name = %s;"
        data = [name]
        self.cursor.execute(query, data)

        equip_id = self.cursor.fetchone()

        if isinstance(equip_id, tuple):
            equip_id = equip_id[0]

        return equip_id

    def get_inventory_id(self, guardian_id):
        query = "SELECT inventory_id FROM inventories WHERE guardian_id = %s;"
        data = [guardian_id]
        self.cursor.execute(query, data)

        inventory_id = self.cursor.fetchone()

        if isinstance(inventory_id, tuple):
            inventory_id = inventory_id[0]

        return inventory_id

    def store_heroes(self, guardian_id, boxes):
        hero_name = ""

        for box in boxes:
            if box.startswith("★★★ "):
                hero_name = box[4:]
            if box.startswith("★★ "):
                hero_name = box[3:]
            if box.startswith("★ "):
                hero_name = box[2:]

            # Get hero ID
            hero_id = self.get_hero_id(hero_name)

            # Get inventory ID
            inventory_id = self.get_inventory_id(guardian_id)

            if not self.is_hero_obtained(guardian_id, hero_id):
                # Enter hero_id in heroes_acquired table
                query = (
                    "INSERT INTO heroes_acquired (hero_id, inventory_id) "
                    + "VALUES (%s, %s);"
                )
                data = [hero_id, inventory_id]
                self.cursor.execute(query, data)
                self.connection.commit()

    def store_equipments(self, guardian_id, boxes):
        equip_name = ""

        for box in boxes:
            if box.startswith("★★★★★ [Ex] "):
                equip_name = box[11:]
            elif box.startswith("★★★★ [Ex] "):
                equip_name = box[10:]
            elif box.startswith("★★★★★ "):
                equip_name = box[6:]
            elif box.startswith("★★★★ "):
                equip_name = box[5:]
            elif box.startswith("★★★ "):
                equip_name = box[4:]
            else:
                equip_name = box[3:]

            # Get equip ID
            equip_id = self.get_equip_id(equip_name)

            # Get inventory ID
            inventory_id = self.get_inventory_id(guardian_id)

            if not self.is_equip_obtained(guardian_id, equip_id):
                # Enter equip_id in equipments_acquired table
                query = (
                    "INSERT INTO equipments_acquired (equip_id, inventory_id) "
                    + "VALUES (%s, %s);"
                )
                data = [equip_id, inventory_id]
                self.cursor.execute(query, data)
                self.connection.commit()

    def get_hero_acquired_details(self, inventory_id, hero_id):
        query = (
            "SELECT hero_acquired_exp, hero_acquired_limit_break "
            + "FROM heroes_acquired "
            + "WHERE hero_id = %s and inventory_id = %s;"
        )
        data = [hero_id, inventory_id]
        self.cursor.execute(query, data)

        heroes_acquired_stats = self.cursor.fetchone()

        exp = heroes_acquired_stats[0]
        level = math.trunc(exp / 100)

        if heroes_acquired_stats:
            hero_acquired = {
                "level": level,
                "exp": exp,
                "limit_break": heroes_acquired_stats[1],
            }
            return hero_acquired
        else:
            return None

    def get_equip_acquired_details(self, inventory_id, equip_id):
        query = (
            "SELECT equip_acquired_exp, equip_acquired_limit_break "
            + "FROM equipments_acquired "
            + "WHERE equip_id = %s and inventory_id = %s;"
        )
        data = [equip_id, inventory_id]
        self.cursor.execute(query, data)

        equipments_acquired_stats = self.cursor.fetchone()

        exp = equipments_acquired_stats[0]
        level = math.trunc(exp / 100)

        if equipments_acquired_stats:
            equip_acquired = {
                "level": level,
                "exp": exp,
                "limit_break": equipments_acquired_stats[1]
            }
            return equip_acquired
        else:
            return None

    def get_hero_stats(self, hero_id):
        query = (
            "SELECT hero_stats, hero_buffs, hero_skill, hero_triggers "
            + "FROM heroes WHERE hero_id = %s;"
        )
        data = [hero_id]
        self.cursor.execute(query, data)
        hero_char = self.cursor.fetchone()

        return hero_char[0], hero_char[1], hero_char[2], hero_char[3]

    def get_equip_stats(self, equip_id):
        query = (
            "SELECT equip_stats, equip_buffs, equip_skill, equip_triggers, "
            + "equip_instant_triggers FROM equipments WHERE equip_id = %s;"
        )
        data = [equip_id]
        self.cursor.execute(query, data)
        equip_char = self.cursor.fetchone()

        return equip_char[0], equip_char[1], \
            equip_char[2], equip_char[3], equip_char[4]

    def get_hero_full_name(self, name):
        heroes = self.get_pool("heroes", "normal", [[], [], []])

        for hero in heroes[2]:
            if name.lower() in hero.lower():
                return hero[4:]

    def get_equip_full_name(self, name):
        equips = self.equipments = self.get_pool(
                "equipments", "normal", [[], [], [], [], []])

        for equip in equips[4]:
            if equip.startswith("★★★★★ [Ex] "):
                if name.lower() in equip.lower():
                    return equip[11:]

    def has_ewp(self, guardian_id, hero_name):
        hero_id = self.get_hero_id(hero_name)

        query = "SELECT equip_id FROM heroes WHERE hero_id = %s;"
        data = [hero_id]
        self.cursor.execute(query, data)
        ewp = self.cursor.fetchone()

        if isinstance(ewp, tuple):
            ewp = ewp[0]

        if self.is_equip_obtained(guardian_id, ewp):
            return True
        else:
            return False

    def get_trophy(self, guardian_id):
        query = "SELECT guardian_trophy FROM guardians WHERE guardian_id = %s;"
        data = [guardian_id]
        self.cursor.execute(query, data)
        trophy = self.cursor.fetchone()

        if isinstance(trophy, tuple):
            trophy = trophy[0]

        return trophy

    def update_trophy(self, guardian_id, trophy):
        trophy = self.get_trophy(guardian_id) + trophy

        query = (
            "UPDATE guardians SET guardian_trophy = %s "
            + "WHERE guardian_id = %s;"
        )
        data = [trophy, guardian_id]

        self.cursor.execute(query, data)
        self.connection.commit()

    def get_hero_exp(self, guardian_id, hero_name):
        hero_id = self.get_hero_id(hero_name)
        inventory_id = self.get_inventory_id(guardian_id)

        query = (
            "SELECT hero_acquired_exp FROM heroes_acquired "
            + "WHERE inventory_id = %s AND hero_id = %s;"
        )
        data = [inventory_id, hero_id]
        self.cursor.execute(query, data)
        exp = self.cursor.fetchone()

        if isinstance(exp, tuple):
            exp = exp[0]

        return exp

    def get_equip_exp(self, guardian_id, equip_name):
        equip_id = self.get_equip_id(equip_name)
        inventory_id = self.get_inventory_id(guardian_id)

        query = (
            "SELECT equip_acquired_exp FROM equipments_acquired "
            + "WHERE inventory_id = %s AND equip_id = %s;"
        )
        data = [inventory_id, equip_id]
        self.cursor.execute(query, data)
        exp = self.cursor.fetchone()

        if isinstance(exp, tuple):
            exp = exp[0]

        return exp

    def get_hero_limit_break(self, guardian_id, hero_name):
        hero_id = self.get_hero_id(hero_name)
        inventory_id = self.get_inventory_id(guardian_id)

        query = (
            "SELECT hero_acquired_limit_break FROM heroes_acquired "
            + "WHERE inventory_id = %s AND hero_id = %s;"
        )
        data = [inventory_id, hero_id]
        self.cursor.execute(query, data)
        lb = self.cursor.fetchone()

        if isinstance(lb, tuple):
            lb = lb[0]

        return lb

    def get_equip_limit_break(self, guardian_id, equip_name):
        equip_id = self.get_equip_id(equip_name)
        inventory_id = self.get_inventory_id(guardian_id)

        query = (
            "SELECT equip_acquired_limit_break FROM equipments_acquired "
            + "WHERE inventory_id = %s AND equip_id = %s;"
        )
        data = [inventory_id, equip_id]
        self.cursor.execute(query, data)
        lb = self.cursor.fetchone()

        if isinstance(lb, tuple):
            lb = lb[0]

        return lb

    def update_hero_exp(self, guardian_id, hero_name, exp):
        hero_id = self.get_hero_id(hero_name)
        inventory_id = self.get_inventory_id(guardian_id)
        exp = self.get_hero_exp(guardian_id, hero_name) + exp
        lb = self.get_hero_limit_break(guardian_id, hero_name)

        level = math.trunc(exp / 100)
        max_level = ((5000 + (5000 * lb)) / 100)

        if level < max_level:
            query = (
                "UPDATE heroes_acquired SET hero_acquired_exp = %s "
                + "WHERE inventory_id = %s AND hero_id = %s;"
            )
            data = [exp, inventory_id, hero_id]
        else:
            query = (
                "UPDATE heroes_acquired SET hero_acquired_exp = %s "
                + "WHERE inventory_id = %s AND hero_id = %s;"
            )
            data = [(5000 + (5000 * lb)), inventory_id, hero_id]

        self.cursor.execute(query, data)
        self.connection.commit()

    def update_equip_exp(self, guardian_id, equip_name, exp):
        equip_id = self.get_equip_id(equip_name)
        inventory_id = self.get_inventory_id(guardian_id)
        exp = self.get_equip_exp(guardian_id, equip_name) + exp
        lb = self.get_equip_limit_break(guardian_id, equip_name)

        level = math.trunc(exp / 100)
        max_level = ((5000 + (5000 * lb)) / 100)

        if level < max_level:
            query = (
                "UPDATE equipments_acquired SET equip_acquired_exp = %s "
                + "WHERE inventory_id = %s AND equip_id = %s;"
            )
            data = [exp, inventory_id, equip_id]
        else:
            query = (
                "UPDATE equipments_acquired SET equip_acquired_exp = %s "
                + "WHERE inventory_id = %s AND equip_id = %s;"
            )
            data = [(5000 + (5000 * lb)), inventory_id, equip_id]

        self.cursor.execute(query, data)
        self.connection.commit()

    def increase_limit_break_hero(self, inventory_id, hero_id, current_lb):
        new_lb = current_lb + 1
        query = (
            "UPDATE heroes_acquired SET hero_acquired_limit_break = %s "
            + "WHERE inventory_id = %s AND hero_id = %s"
        )
        data = [new_lb, inventory_id, hero_id]
        self.cursor.execute(query, data)
        self.connection.commit()

    def increase_limit_break_equip(self, inventory_id, equip_id, current_lb):
        new_lb = current_lb + 1
        query = (
            "UPDATE equipments_acquired SET equip_acquired_limit_break = %s "
            + "WHERE inventory_id = %s AND equip_id = %s"
        )
        data = [new_lb, inventory_id, equip_id]
        self.cursor.execute(query, data)
        self.connection.commit()

    def get_hourly_qualification(self, guardian_id):
        query = "SELECT guardian_hourly FROM guardians WHERE guardian_id = %s;"
        data = [guardian_id]
        self.cursor.execute(query, data)

        last_hour = self.cursor.fetchone()
        now = datetime.now(pytz.utc)

        if isinstance(last_hour, tuple):
            last_hour = last_hour[0]

        if last_hour:
            difference = now - last_hour

            if difference.total_seconds() > 3600:
                query = (
                    "UPDATE guardians SET guardian_hourly = %s "
                    + "WHERE guardian_id = %s;"
                )
                data = [now, guardian_id]
                self.cursor.execute(query, data)
                self.connection.commit()

                return True
            else:
                return False
        else:
            query = (
                "UPDATE guardians SET guardian_hourly = %s "
                + "WHERE guardian_id = %s;"
            )
            data = [now, guardian_id]
            self.cursor.execute(query, data)
            self.connection.commit()

            return True

    def get_hourly_cooldown(self, guardian_id):
        query = "SELECT guardian_hourly FROM guardians WHERE guardian_id = %s;"
        data = [guardian_id]
        self.cursor.execute(query, data)

        last_hour = self.cursor.fetchone()
        now = datetime.now(pytz.utc)

        if isinstance(last_hour, tuple):
            last_hour = last_hour[0]

        if last_hour:
            difference = now - last_hour

            if difference.total_seconds() > 3600:
                return 0
            else:
                time_to_reset = 3600 - difference.total_seconds()

                if time_to_reset >= 60:
                    time_to_reset = time.gmtime(time_to_reset)
                    cd = time.strftime(
                        "%-Mm and %-Ss", time_to_reset)
                else:
                    time_to_reset = time.gmtime(time_to_reset)
                    cd = time.strftime("%-Ss", time_to_reset)

                return cd
        else:
            return 0

    def get_daily_count(self, guardian_id):
        query = (
            "SELECT guardian_daily_count FROM guardians "
            + "WHERE guardian_id = %s;"
        )
        data = [guardian_id]
        self.cursor.execute(query, data)
        count = self.cursor.fetchone()

        if isinstance(count, tuple):
            count = count[0]

        return count

    def increase_daily_count(self, guardian_id):
        count = self.get_daily_count(guardian_id)

        count = count + 1

        query = (
            "UPDATE guardians SET guardian_daily_count = %s "
            + "WHERE guardian_id = %s;"
        )
        data = [count, guardian_id]
        self.cursor.execute(query, data)
        self.connection.commit()

    def get_daily_qualification(self, guardian_id):
        query = "SELECT guardian_daily FROM guardians WHERE guardian_id = %s;"
        data = [guardian_id]
        self.cursor.execute(query, data)

        last_day = self.cursor.fetchone()
        now = datetime.now(pytz.utc)

        if isinstance(last_day, tuple):
            last_day = last_day[0]

        if last_day:
            difference = now - last_day

            if difference.total_seconds() > 86400:
                query = (
                    "UPDATE guardians SET guardian_daily = %s "
                    + "WHERE guardian_id = %s;"
                )
                data = [now, guardian_id]
                self.cursor.execute(query, data)
                self.connection.commit()
                self.increase_daily_count(guardian_id)

                return True
            else:
                return False
        else:
            query = (
                "UPDATE guardians SET guardian_daily = %s "
                + "WHERE guardian_id = %s;"
            )
            data = [now, guardian_id]
            self.cursor.execute(query, data)
            self.connection.commit()
            self.increase_daily_count(guardian_id)

            return True

    def get_daily_cooldown(self, guardian_id):
        query = "SELECT guardian_daily FROM guardians WHERE guardian_id = %s;"
        data = [guardian_id]
        self.cursor.execute(query, data)

        last_day = self.cursor.fetchone()
        now = datetime.now(pytz.utc)

        if isinstance(last_day, tuple):
            last_day = last_day[0]

        if last_day:
            difference = now - last_day

            if difference.total_seconds() > 86400:
                return 0
            else:
                time_to_reset = 86400 - difference.total_seconds()

                if time_to_reset >= 3600:
                    time_to_reset = time.gmtime(time_to_reset)
                    cd = time.strftime(
                        "%-Hh, %-Mm, and %-Ss", time_to_reset)
                elif time_to_reset >= 60:
                    time_to_reset = time.gmtime(time_to_reset)
                    cd = time.strftime(
                        "%-Mm and %-Ss", time_to_reset)
                else:
                    time_to_reset = time.gmtime(time_to_reset)
                    cd = time.strftime("%-Ss", time_to_reset)

                return cd
        else:
            return 0

    def get_spent_gems(self, guardian_id):
        query = (
            "SELECT guardian_spent_gems FROM guardians "
            + "WHERE guardian_id = %s;"
        )
        data = [guardian_id]
        self.cursor.execute(query, data)

        spent_gems = self.cursor.fetchone()

        if isinstance(spent_gems, tuple):
            spent_gems = spent_gems[0]

        return spent_gems

    def store_spent_gems(self, guardian_id, gems):
        spent_gems = self.get_spent_gems(guardian_id)

        spent_gems = spent_gems + gems

        query = (
            "UPDATE guardians SET guardian_spent_gems = %s "
            + "WHERE guardian_id = %s;"
        )
        data = [spent_gems, guardian_id]
        self.cursor.execute(query, data)
        self.connection.commit()

    def get_gambled_gems(self, guardian_id):
        query = (
            "SELECT guardian_gambled_gems FROM guardians "
            + "WHERE guardian_id = %s;"
        )
        data = [guardian_id]
        self.cursor.execute(query, data)

        gambled_gems = self.cursor.fetchone()

        if isinstance(gambled_gems, tuple):
            gambled_gems = gambled_gems[0]

        return gambled_gems

    def store_gambled_gems(self, guardian_id, gems):
        gambled_gems = self.get_gambled_gems(guardian_id)

        gambled_gems = gambled_gems + gems

        query = (
            "UPDATE guardians SET guardian_gambled_gems = %s "
            + "WHERE guardian_id = %s;"
        )
        data = [gambled_gems, guardian_id]
        self.cursor.execute(query, data)
        self.connection.commit()

    def get_arena_wins(self, guardian_id):
        query = "SELECT guardian_wins FROM guardians WHERE guardian_id = %s;"
        data = [guardian_id]
        self.cursor.execute(query, data)

        arena_wins = self.cursor.fetchone()

        if isinstance(arena_wins, tuple):
            arena_wins = arena_wins[0]

        return arena_wins

    def increase_arena_wins(self, guardian_id):
        arena_wins = self.get_arena_wins(guardian_id)

        arena_wins = arena_wins + 1

        query = (
            "UPDATE guardians SET guardian_wins = %s "
            + "WHERE guardian_id = %s;"
        )
        data = [arena_wins, guardian_id]
        self.cursor.execute(query, data)
        self.connection.commit()

    def get_arena_losses(self, guardian_id):
        query = "SELECT guardian_losses FROM guardians WHERE guardian_id = %s;"
        data = [guardian_id]
        self.cursor.execute(query, data)

        arena_losses = self.cursor.fetchone()

        if isinstance(arena_losses, tuple):
            arena_losses = arena_losses[0]

        return arena_losses

    def increase_arena_losses(self, guardian_id):
        arena_losses = self.get_arena_losses(guardian_id)

        arena_losses = arena_losses + 1

        query = (
            "UPDATE guardians SET guardian_losses = %s "
            + "WHERE guardian_id = %s;"
        )
        data = [arena_losses, guardian_id]
        self.cursor.execute(query, data)
        self.connection.commit()

    def get_user_exp(self, guardian_id):
        query = (
            "SELECT guardian_exp FROM guardians "
            + "WHERE guardian_id = %s;"
        )
        data = [guardian_id]
        self.cursor.execute(query, data)
        user_exp = self.cursor.fetchone()

        if isinstance(user_exp, tuple):
            user_exp = user_exp[0]

        return user_exp

    def update_user_exp(self, guardian_id, exp):
        user_exp = self.get_user_exp(guardian_id)
        user_exp = user_exp + exp

        # Set max level
        max_level = 482
        max_exp = max_level * 100

        if user_exp >= max_exp:
            user_exp = max_exp

        query = (
            "UPDATE guardians SET guardian_exp = %s "
            + "WHERE guardian_id = %s;"
        )
        data = [user_exp, guardian_id]
        self.cursor.execute(query, data)
        self.connection.commit()

    def get_user_level(self, guardian_id):
        user_exp = self.get_user_exp(guardian_id)

        level = math.trunc(user_exp / 100)

        return level

    def get_won_gambled_gems(self, guardian_id):
        query = (
            "SELECT guardian_won_gambled_gems FROM guardians "
            + "WHERE guardian_id = %s;"
        )
        data = [guardian_id]
        self.cursor.execute(query, data)

        won_gambled_gems = self.cursor.fetchone()

        if isinstance(won_gambled_gems, tuple):
            won_gambled_gems = won_gambled_gems[0]

        return won_gambled_gems

    def store_won_gambled_gems(self, guardian_id, gems):
        won_gambled_gems = self.get_won_gambled_gems(guardian_id)

        won_gambled_gems = won_gambled_gems + gems

        query = (
            "UPDATE guardians SET guardian_won_gambled_gems = %s "
            + "WHERE guardian_id = %s;"
        )
        data = [won_gambled_gems, guardian_id]
        self.cursor.execute(query, data)
        self.connection.commit()

    def get_lose_gambled_gems(self, guardian_id):
        query = (
            "SELECT guardian_lose_gambled_gems FROM guardians "
            + "WHERE guardian_id = %s;"
        )
        data = [guardian_id]
        self.cursor.execute(query, data)

        lose_gambled_gems = self.cursor.fetchone()

        if isinstance(lose_gambled_gems, tuple):
            lose_gambled_gems = lose_gambled_gems[0]

        return lose_gambled_gems

    def store_lose_gambled_gems(self, guardian_id, gems):
        lose_gambled_gems = self.get_lose_gambled_gems(guardian_id)

        lose_gambled_gems = lose_gambled_gems + gems

        query = (
            "UPDATE guardians SET guardian_lose_gambled_gems = %s "
            + "WHERE guardian_id = %s;"
        )
        data = [lose_gambled_gems, guardian_id]
        self.cursor.execute(query, data)
        self.connection.commit()

    def get_lose_gambled_count(self, guardian_id):
        query = (
            "SELECT guardian_lose_gambled_count FROM guardians "
            + "WHERE guardian_id = %s;"
        )
        data = [guardian_id]
        self.cursor.execute(query, data)

        lose_gambled_count = self.cursor.fetchone()

        if isinstance(lose_gambled_count, tuple):
            lose_gambled_count = lose_gambled_count[0]

        return lose_gambled_count

    def store_lose_gambled_count(self, guardian_id):
        lose_gambled_count = self.get_lose_gambled_count(guardian_id)

        lose_gambled_count = lose_gambled_count + 1

        query = (
            "UPDATE guardians SET guardian_lose_gambled_count = %s "
            + "WHERE guardian_id = %s;"
        )
        data = [lose_gambled_count, guardian_id]
        self.cursor.execute(query, data)
        self.connection.commit()

    def get_won_gambled_count(self, guardian_id):
        query = (
            "SELECT guardian_won_gambled_count FROM guardians "
            + "WHERE guardian_id = %s;"
        )
        data = [guardian_id]
        self.cursor.execute(query, data)

        won_gambled_count = self.cursor.fetchone()

        if isinstance(won_gambled_count, tuple):
            won_gambled_count = won_gambled_count[0]

        return won_gambled_count

    def store_won_gambled_count(self, guardian_id):
        won_gambled_count = self.get_won_gambled_count(guardian_id)

        won_gambled_count = won_gambled_count + 1

        query = (
            "UPDATE guardians SET guardian_won_gambled_count = %s "
            + "WHERE guardian_id = %s;"
        )
        data = [won_gambled_count, guardian_id]
        self.cursor.execute(query, data)
        self.connection.commit()

    def get_gamble_count(self, guardian_id):
        query = (
            "SELECT guardian_gamble_count FROM guardians "
            + "WHERE guardian_id = %s;"
        )
        data = [guardian_id]
        self.cursor.execute(query, data)

        gamble_count = self.cursor.fetchone()

        if isinstance(gamble_count, tuple):
            gamble_count = gamble_count[0]

        return gamble_count

    def store_gamble_count(self, guardian_id):
        gamble_count = self.get_gamble_count(guardian_id)

        gamble_count = gamble_count + 1

        query = (
            "UPDATE guardians SET guardian_gamble_count = %s "
            + "WHERE guardian_id = %s;"
        )
        data = [gamble_count, guardian_id]
        self.cursor.execute(query, data)
        self.connection.commit()

    def get_summon_count(self, guardian_id):
        query = (
            "SELECT guardian_summon_count FROM guardians "
            + "WHERE guardian_id = %s;"
        )
        data = [guardian_id]
        self.cursor.execute(query, data)

        summon_count = self.cursor.fetchone()

        if isinstance(summon_count, tuple):
            summon_count = summon_count[0]

        return summon_count

    def store_summon_count(self, guardian_id, count):
        summon_count = self.get_summon_count(guardian_id)

        summon_count = summon_count + count

        query = (
            "UPDATE guardians SET guardian_summon_count = %s "
            + "WHERE guardian_id = %s;"
        )
        data = [summon_count, guardian_id]
        self.cursor.execute(query, data)
        self.connection.commit()

    def get_exclusive_weapon_id(self, hero_id):
        query = "SELECT equip_id FROM heroes WHERE hero_id = %s;"
        data = [hero_id]
        self.cursor.execute(query, data)
        equip_id = self.cursor.fetchone()

        if isinstance(equip_id, tuple):
            equip_id = equip_id[0]

        return equip_id

    def get_hero_id_for_exclusive_weapon(self, equip_id):
        query = "SELECT hero_id FROM heroes WHERE equip_id = %s;"
        data = [equip_id]
        self.cursor.execute(query, data)
        hero_id = self.cursor.fetchone()

        if isinstance(hero_id, tuple):
            hero_id = hero_id[0]

        return hero_id

    def get_item_id(self, item_name):
        shop_items = self.get_shop_items()

        for shop_item in shop_items:
            if item_name.lower() in shop_item[0].lower():
                query = "SELECT item_id FROM items WHERE item_name = %s;"
                data = [shop_item[0]]
                self.cursor.execute(query, data)
                item_id = self.cursor.fetchone()

                if isinstance(item_id, tuple):
                    item_id = item_id[0]

                return item_id

    def get_shop_items(self):
        query = "SELECT item_name, item_price FROM items;"
        self.cursor.execute(query)
        shop_items = self.cursor.fetchall()

        return shop_items

    def get_shop_item_detailed(self, item_name):
        item_id = self.get_item_id(item_name)

        if not item_id:
            return None

        query = (
            "SELECT item_name, item_price, item_description "
            + "FROM items WHERE item_id = %s;"
        )
        data = [item_id]
        self.cursor.execute(query, data)
        shop_item = self.cursor.fetchone()

        return shop_item

    def buy_items(self, guardian_id, item_name, amount):
        item_id = self.get_item_id(item_name)
        inventory_id = self.get_inventory_id(guardian_id)

        query = (
            "SELECT item_acquired_quantity FROM items_acquired "
            + "WHERE item_id = %s AND inventory_id = %s;"
        )
        data = [item_id, inventory_id]
        self.cursor.execute(query, data)

        item_already_in = self.cursor.fetchone()

        if isinstance(item_already_in, tuple):
            item_already_in = item_already_in[0]

        if item_already_in is None:
            query = (
                "INSERT INTO items_acquired "
                + "(item_id, inventory_id, item_acquired_quantity) "
                + "VALUES (%s, %s, %s);"
            )
            data = [item_id, inventory_id, amount]
        else:
            query = (
                "UPDATE items_acquired SET "
                + "item_acquired_quantity = item_acquired_quantity + %s "
                + "WHERE item_id = %s AND inventory_id = %s;"
            )
            data = [amount, item_id, inventory_id]

        self.cursor.execute(query, data)
        self.connection.commit()



    # Disconnect database
    def disconnect(self):
        self.cursor.close()
        self.connection.close()
