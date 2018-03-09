import pydig
import random; random.seed()

SMTP_SERVER_NAME = 'smtp.gmail.com'
SMTP_SERVERS = pydig.dig(SMTP_SERVER_NAME)
#print SMTP_SERVERS
SMTP_SERVER = SMTP_SERVERS[0]
SMTP_PORT = 587

# Use this when collecting students submission
USER = "ciss430recipe01@gmail.com"
PASSWORD = "recipesite01"

