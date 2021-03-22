#!/usr/bin/env python

import os
import sqlite3
import datetime


class Database:
    def __init__(self):
        # If file is present in the first place
        if os.path.isfile("ailie.db"):
            self.connection = sqlite3.connect(
                "ailie.db",
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            )
            self.cursor = self.connection.cursor()
        # If the file is not present then the tables is created along with the database
        else:
            self.connection = sqlite3.connect(
                "ailie.db",
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            )
            self.cursor = self.connection.cursor()

            # Create all the tables
            with open("ailie.sql") as file:
                lines = file.readlines()
                for l in lines:
                    self.cursor.execute(l)
                self.connection.commit()

    def disconnect(self):
        self.cursor.close()
        self.connection.close()

    def getGuardianInfo(self, id):
        # Initialize guardian info
        guardian_info = {}

        # Query guardian details
        query = "SELECT * FROM guardians WHERE id = ?;"
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
        pull_time = datetime.datetime.now()

        # Check value of gems
        if count == "10" or count.lower() == "ten":
            gems = 2700
        else:
            gems = 300

        # Insert value accordingly for first pull
        query = (
            "INSERT INTO guardians (id, tmp_gems, total_gems, last_pull) "
            + "VALUES (?, ?, ?, ?);"
        )
        data = (id, gems, gems, pull_time)
        self.cursor.execute(query, data)
        self.connection.commit()

    def secondOrMorePulls(self, id, count, tmp_gems, total_gems):
        # Initialize pull timestamp
        pull_time = datetime.datetime.now()

        # Gems check per session and total
        if count == "10" or count.lower() == "ten":
            gems = 2700
        else:
            gems = 300

        tmp_gems = tmp_gems + gems
        total_gems = total_gems + gems

        # Update the value accordingly
        query = (
            "UPDATE guardians SET tmp_gems = ?, total_gems = ?, "
            + "last_pull = ? WHERE id = ?;"
        )
        data = (tmp_gems, total_gems, pull_time, id)
        self.cursor.execute(query, data)
        self.connection.commit()

    def checkTimeExpired(self, id):
        last_pull = datetime.datetime.now()

        # Query guardian details
        query = "SELECT last_pull FROM guardians WHERE id = ?;"
        data = [id]
        self.cursor.execute(query, data)

        # Get the details if present
        row = self.cursor.fetchone()
        if row:
            last_pull = row[0]

        # Calculate how long has it been since last pull
        time_now = datetime.datetime.now()
        period = time_now - last_pull

        if period.total_seconds() > 600:
            query = "UPDATE guardians SET tmp_gems = ? WHERE id = ?;"
            data = (0, id)
            self.cursor.execute(query, data)
            self.connection.commit()
            return True
        else:
            return False
