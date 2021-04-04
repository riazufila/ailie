#!/usr/bin/env python

import os
import psycopg2


class Database():
    def __init__(self):
        DATABASE_URL = os.environ["DATABASE_URL"]
        self.connection = psycopg2.connect(DATABASE_URL, sslmode="require")
        self.cursor = self.connection.cursor()

    # Guardians related query
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

    # Guilds related query
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
        query = "UPDATE guardians SET guild_id = NULL WHERE guild_id = %s;"
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

    # Currency related query
    def store_gems(self, guardian_id, gems):
        # Get already existing gems
        query = "SELECT guardian_gems FROM guardians WHERE guardian_id = %s;"
        data = [guardian_id]
        self.cursor.execute(query, data)

        row = self.cursor.fetchone()

        if isinstance(row, tuple):
            row = row[0]

        # Add total gems
        gems = row + gems

        # Update into database
        query = (
            "UPDATE guardians SET guardian_gems = %s WHERE guardian_id = %s;"
        )
        data = [gems, guardian_id]
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

    # Summons related query
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
            "SELECT h.hero_star, h.hero_name FROM guardians g "
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

        for hero in hero_inventory:
            if hero[0] == 3:
                hero_buffer[2].append("★★★ " + hero[1])
            if hero[0] == 2:
                hero_buffer[1].append("★★ " + hero[1])
            if hero[0] == 1:
                hero_buffer[0].append("★ " + hero[1])

        return hero_buffer

    def equip_inventory(self, guardian_id):
        query = (
            "SELECT eq.equip_star, eq.equip_exclusive, eq.equip_name "
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

        for equip in equip_inventory:
            if equip[1]:
                if equip[0] == 5:
                    equip_buffer[5].append("★★★★★ [Ex] " + equip[2])
                if equip[0] == 4:
                    equip_buffer[4].append("★★★★ [Ex] " + equip[2])
            else:
                if equip[0] == 5:
                    equip_buffer[3].append("★★★★★ " + equip[2])
                if equip[0] == 4:
                    equip_buffer[2].append("★★★★ " + equip[2])
                if equip[0] == 3:
                    equip_buffer[1].append("★★★ " + equip[2])
                if equip[0] == 2:
                    equip_buffer[0].append("★★ " + equip[2])

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

    # Disconnect database
    def disconnect(self):
        self.cursor.close()
        self.connection.close()
