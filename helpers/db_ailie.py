#!/usr/bin/env python

import os
import sys
import random
import psycopg2


class DatabaseAilie:
    def __init__(self):
        if sys.argv[1] == "production":
            # Production database
            DATABASE_URL = os.environ["DATABASE_URL"]
            self.connection = psycopg2.connect(DATABASE_URL, sslmode="require")
        else:
            # Development database
            self.connection = psycopg2.connect(
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
            )

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
            inventory_check = True
            inventory_id = 0

            while inventory_check:
                inventory_id = random.randint(pow(10, 14), (pow(10, 15) - 1))
                inventory_check = self.inventory_exists(inventory_id)

            query = "INSERT INTO inventories (inventory_id) VALUES (%s);"
            data = [inventory_id]
            self.cursor.execute(query, data)

            query = "INSERT INTO guardians (guardian_id, inventory_id) VALUES (%s, %s);"
            data = [guardian_id, inventory_id]
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
            query = "UPDATE guardians SET guardian_gems = %s WHERE guardian_id = %s;"
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

    def inventory_exists(self, inventory_id):
        query = "SELECT inventory_id FROM guardians WHERE inventory_id = %s;"
        data = [inventory_id]
        self.cursor.execute(query, data)

        row = self.cursor.fetchone()

        if isinstance(row, tuple):
            row = row[0]

        if row:
            return True
        else:
            return False

    # def store_heroes(self, inventory_id, boxes):

    #     for box in boxes:

    #     return

    # Disconnect database
    def disconnect(self):
        self.cursor.close()
        self.connection.close()
