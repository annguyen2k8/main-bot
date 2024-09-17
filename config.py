import os
from dotenv import load_dotenv, dotenv_values 
load_dotenv() 

token = os.getenv('TOKEN')
command_prefix = ('s!')