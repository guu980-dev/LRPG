import gradio as gr
import random
from langchain_chroma import Chroma
from langchain_upstage import UpstageEmbeddings
from langchain.docstore.document import Document
from langchain_core.prompts import PromptTemplate
from langchain_upstage import ChatUpstage
import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from generate_image import generate_image, download_image
import requests
from IPython.display import display, Image
from langchain_community.vectorstores.oraclevs import OracleVS
import oracledb
from langchain_community.vectorstores.utils import DistanceStrategy


dotenv_path = os.path.join(os.path.dirname(__file__), '.env') # Path to the .env file
load_dotenv(dotenv_path) # Load the environment variables from the .env file

