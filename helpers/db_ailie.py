#!/usr/bin/env python

import os
import psycopg2


class DatabaseAilie:
    def __init__(self, stage, guardian_id):
        if stage.lower() == "production":
            # Production database
            DATABASE_URL = os.environ["DATABASE_URL"]
            self.connection = psycopg2.connect(DATABASE_URL, sslmode="require")
        elif stage.lower() == "development":
            # Development database
            self.connection = psycopg2.connect(
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
            )
        else:
            exit()

        self.cursor = self.connection.cursor()
        self.initialize_user(guardian_id)

    def initialize_user(self, guardian_id):
        initialized = False

        query = "SELECT guardian_id FROM guardians WHERE guardian_id = %s;"
        data = [guardian_id]
        self.cursor.execute(query, data)
        row = self.cursor.fetchone()
        if row[0]:
            initialized = True
        else:
            initialized = False

        if not initialized:
            query = "INSERT INTO guardians (guardian_id) VALUES (%s);"
            data = [guardian_id]
            self.cursor.execute(query, data)
            self.connection.commit()

    def disconnect(self):
        self.cursor.close()
        self.connection.close()
