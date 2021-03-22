#!/usr/bin/env python

import os
import psycopg2
from datetime import datetime, timezone


class Database:
    def __init__(self):
        # Production database connect
        DATABASE_URL = os.environ["DATABASE_URL"]
        self.connection = psycopg2.connect(DATABASE_URL, sslmode="require")

        # Development local database connect
        # self.connection = psycopg2.connect(
        #     database=os.getenv("DB_NAME"),
        #     user=os.getenv("DB_USER"),
        #     password=os.getenv("DB_PASSWORD"),
        #     host=os.getenv("DB_HOST"),
        #     port=os.getenv("DB_PORT"),
        # )

        self.cursor = self.connection.cursor()

    def disconnect(self):
        self.cursor.close()
        self.connection.close()

    def getGuardianInfo(self, id):
        # Initialize guardian info
        guardian_info = {}

        # Query guardian details
        query = "SELECT * FROM guardians WHERE user_id = %s;"
        data = [id]
        self.cursor.execute(query, data)

        # Get the details if present
        row = self.cursor.fetchone()
        if row:
            guardian_info["tmp_gems"] = row[1]
            guardian_info["total_gems"] = row[2]

        return guardian_info

    def firstPull(self, id, count):
        # Initialize pull timestamp
        pull_time = datetime.now(timezone.utc)

        # Check value of gems
        if count == "10" or count.lower() == "ten":
            gems = 2700
        else:
            gems = 300

        # Insert value accordingly for first pull
        query = (
            "INSERT INTO guardians (user_id, tmp_gems, total_gems, last_pull) "
            + "VALUES (%s, %s, %s, %s);"
        )
        data = (id, gems, gems, pull_time)
        self.cursor.execute(query, data)
        self.connection.commit()

    def secondOrMorePulls(self, id, count, tmp_gems, total_gems):
        # Initialize pull timestamp
        pull_time = datetime.now(timezone.utc)

        # Gems check per session and total
        if count == "10" or count.lower() == "ten":
            gems = 2700
        else:
            gems = 300

        tmp_gems = tmp_gems + gems
        total_gems = total_gems + gems

        # Update the value accordingly
        query = (
            "UPDATE guardians SET tmp_gems = %s, total_gems = %s, "
            + "last_pull = %s WHERE user_id = %s;"
        )
        data = (tmp_gems, total_gems, pull_time, id)
        self.cursor.execute(query, data)
        self.connection.commit()

    def checkTimeExpired(self, id):
        last_pull = None

        # Query guardian details
        query = "SELECT last_pull FROM guardians WHERE user_id = %s;"
        data = [id]
        self.cursor.execute(query, data)

        # Get the details if present
        row = self.cursor.fetchone()
        if row:
            last_pull = row[0]

        # Calculate how long has it been since last pull
        time_now = datetime.now(timezone.utc)
        period = time_now - last_pull

        if period.total_seconds() > 600:
            query = "UPDATE guardians SET tmp_gems = %s WHERE user_id = %s;"
            data = (0, id)
            self.cursor.execute(query, data)
            self.connection.commit()
            return True
        else:
            return False
