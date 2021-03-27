#!/usr/bin/env python

import os
import sys
import psycopg2


class DatabaseAilie:
    def __init__(self, guardian_id):
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
        self.initialize_user(guardian_id)

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
        return row[0]

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

    def get_guild_id_of_member(self, guardian_id):
        query = "SELECT guild_id FROM guardians WHERE guardian_id = %s;"
        data = [guardian_id]
        self.cursor.execute(query, data)
        row = self.cursor.fetchone()

        if isinstance(row, tuple):
            row = row[0]

        guild_id = row

        return guild_id

    def quit_guild(self, guardian_id):
        query = "UPDATE guardians SET guild_id = NULL WHERE guardian_id = %s;"
        data = [guardian_id]
        self.cursor.execute(query, data)
        self.connection.commit()

    def disconnect(self):
        self.cursor.close()
        self.connection.close()
