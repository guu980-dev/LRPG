import os, requests, time
import oracledb
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)
from langchain_upstage import UpstageLayoutAnalysisLoader
from bs4 import BeautifulSoup
from langchain_core.documents import BaseDocumentTransformer, Document
from langchain_upstage import UpstageEmbeddings
from langchain_community.vectorstores.oraclevs import OracleVS
from langchain_community.vectorstores.utils import DistanceStrategy


def upload_db_harrypotter():
  global retriever

  username=os.environ["DB_USER"]
  password=os.environ["DB_PASSWORD"]
  dsn=os.environ["DSN"]

  con = oracledb.connect(user=username, password=password, dsn=dsn)

  try: 
      conn23c = oracledb.connect(user=username, password=password, dsn=dsn)
      print("Connection successful!", conn23c.version)
  except Exception as e:
      print("Connection failed!")

  file_path = "./Harry Potter and the Sorcerers Stone.pdf" # Path to the PDF file
  #file_path = "https://en.wikipedia.org/wiki/Donald_Trump"

  text_splitter = RecursiveCharacterTextSplitter.from_language(
      chunk_size=1500, chunk_overlap=200, language=Language.HTML
  )

  if file_path.endswith(".pdf"): # Check if the document is PDF
      #print("pdf file")
      layzer = UpstageLayoutAnalysisLoader(file_path, split="page")

      # For improved memory efficiency, consider using the lazy_load method to load documents page by page.
      docs = layzer.load()  # or layzer.lazy_load()

      docs = text_splitter.split_documents(docs)
  elif file_path.startswith("http"): # Check if the document is from a website
      #print("url")
      # Specify the URL of the Wikipedia page you want to scrape
      url = file_path

      # Send a GET request to the URL
      response = requests.get(url)

      # Create a BeautifulSoup object to parse the HTML content
      soup = BeautifulSoup(response.content, "html.parser")

      # Find the main content element on the page
      content = soup.find(id="mw-content-text")

      # Attempt to find and remove the unnecessary section by looking for common identifiers
      for section_id in ["References", "references", "See_also", "External_links", "Footnotes", "Further_reading"]:
          elements = content.find(id=section_id)
          if elements:
              elements.decompose()

      for section_class in ["reflist", "references", "navbox",]:
          elements = content.find_all(class_=section_class)
          for element in elements:
              element.decompose()

      # Extract the text from the modified content element
      text = content.get_text()

      docs = Document(page_content=text)

      docs = text_splitter.split_documents([docs])  

  upstage_embeddings = UpstageEmbeddings(model="solar-embedding-1-large")
      
  # Configure the vector store with the model, table name, and using the indicated distance strategy for the similarity search and vectorize the chunks
  s1time = time.time()

  knowledge_base = OracleVS.from_documents(docs, upstage_embeddings, client=conn23c, 
                      table_name="text_embeddings_HarryPotter", 
                      distance_strategy=DistanceStrategy.DOT_PRODUCT)    

  s2time =  time.time()      
  #print( f"Vectorizing and inserting chunks duration: {round(s2time - s1time, 1)} sec.")

  vector_store = OracleVS(client=conn23c, 
                          embedding_function=upstage_embeddings, 
                          table_name="text_embeddings_HarryPotter", 
                          distance_strategy=DistanceStrategy.DOT_PRODUCT)

  retriever = vector_store.as_retriever()


def upload_db_Trump():
  global retriever

  username=os.environ["DB_USER"]
  password=os.environ["DB_PASSWORD"]
  dsn=os.environ["DSN"]

  con = oracledb.connect(user=username, password=password, dsn=dsn)

  try: 
      conn23c = oracledb.connect(user=username, password=password, dsn=dsn)
      print("Connection successful!", conn23c.version)
  except Exception as e:
      print("Connection failed!")

#   file_path = "./Harry Potter and the Sorcerers Stone.pdf" # Path to the PDF file
  file_path = "https://en.wikipedia.org/wiki/Donald_Trump"

  text_splitter = RecursiveCharacterTextSplitter.from_language(
      chunk_size=1500, chunk_overlap=200, language=Language.HTML
  )

  if file_path.endswith(".pdf"): # Check if the document is PDF
      #print("pdf file")
      layzer = UpstageLayoutAnalysisLoader(file_path, split="page")

      # For improved memory efficiency, consider using the lazy_load method to load documents page by page.
      docs = layzer.load()  # or layzer.lazy_load()

      docs = text_splitter.split_documents(docs)
  elif file_path.startswith("http"): # Check if the document is from a website
      #print("url")
      # Specify the URL of the Wikipedia page you want to scrape
      url = file_path

      # Send a GET request to the URL
      response = requests.get(url)

      # Create a BeautifulSoup object to parse the HTML content
      soup = BeautifulSoup(response.content, "html.parser")

      # Find the main content element on the page
      content = soup.find(id="mw-content-text")

      # Attempt to find and remove the unnecessary section by looking for common identifiers
      for section_id in ["References", "references", "See_also", "External_links", "Footnotes", "Further_reading"]:
          elements = content.find(id=section_id)
          if elements:
              elements.decompose()

      for section_class in ["reflist", "references", "navbox",]:
          elements = content.find_all(class_=section_class)
          for element in elements:
              element.decompose()

      # Extract the text from the modified content element
      text = content.get_text()

      docs = Document(page_content=text)

      docs = text_splitter.split_documents([docs])  

  upstage_embeddings = UpstageEmbeddings(model="solar-embedding-1-large")
      
  # Configure the vector store with the model, table name, and using the indicated distance strategy for the similarity search and vectorize the chunks
  s1time = time.time()

  knowledge_base = OracleVS.from_documents(docs, upstage_embeddings, client=conn23c, 
                      table_name="text_embeddings_Trump", 
                      distance_strategy=DistanceStrategy.DOT_PRODUCT)    

  s2time =  time.time()      
  #print( f"Vectorizing and inserting chunks duration: {round(s2time - s1time, 1)} sec.")

  vector_store = OracleVS(client=conn23c, 
                          embedding_function=upstage_embeddings, 
                          table_name="text_embeddings_Trump", 
                          distance_strategy=DistanceStrategy.DOT_PRODUCT)

  retriever = vector_store.as_retriever()


def main():
    upload_db_harrypotter()

if __name__ == "__main__":
    main()