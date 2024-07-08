import sqlite3
import ccxt
import logging
from datetime import datetime
import threading

# Class to handle thread-local SQLite connection
class ThreadLocalDatabase:
    def __init__(self):
        self.local = threading.local()
        
    def get_connection(self):
        if not hasattr(self.local, 'connection'):
            self.local.connection = sqlite3.connect('app.db', check_same_thread=False)
        return self.local.connection

# Create a single instance of ThreadLocalDatabase
thread_local_db = ThreadLocalDatabase()