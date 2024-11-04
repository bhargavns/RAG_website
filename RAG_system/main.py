import os
import time
import logging
import json
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.embeddings import HuggingFaceEmbeddings

from GlossObfuscator import GlossObfuscator
from RagChainCreator import RagChainCreator
from VectorStore import VectorStore

from correction_template import correction_template_blank, correction_template_random, correction_prompt_blank, correction_prompt_random

import argparse

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

def load_documents(file_path):
    loader = PyPDFLoader(file_path=file_path)
    return loader.load()

def create_embeddings():
    try:
        return OpenAIEmbeddings()
    except Exception as e:
        logging.warning(f"Failed to create OpenAIEmbeddings: {e}. Falling back to HuggingFaceEmbeddings.")
        return HuggingFaceEmbeddings()

def process_file(input_file):
    """
    Given an input file containing \g, \\t, and \m lines, returns a list of dictionaries
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    input_documents = []
    current_gloss = dict()

    for line in lines:
        if line.startswith('\g'):
            current_gloss['gloss'] = line.strip()[3:]
        elif line.startswith('\\t'):
            current_gloss['text'] = line.strip()[3:]
        elif line.startswith('\m'):
            current_gloss['morphemes'] = line.strip()[3:]
        elif line.startswith('\l'):
            current_gloss['translation'] = line.strip()[3:]
        # Check if we have all the required fields
        if not line.strip():
            input_documents.append(current_gloss)
            current_gloss = dict()
    input_documents = [doc for doc in input_documents if doc]
    return input_documents

def main():
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument('--model', type=str, default='claude-3-5-sonnet-20240620', help='Model selection')
    parser.add_argument('--obfuscation_style', type=str, default='blank', help='Obfuscation style selector')
    parser.add_argument('--obfuscation_percentage', type=int, default=40, help='Percentage of obfuscation')
    parser.add_argument('--language', type=str, default='Arapaho', help='Language to process')
    args = parser.parse_args()

    lang = args.language
    reference_doc = f'./ReferenceDocs/{lang}Ref.pdf'
    
    logging.info(f"Loading {lang} reference document...")
    docs = load_documents(reference_doc)
    
    logging.info("Creating vectorstore...")
    try:
        vectorstore = VectorStore(chunk_size=800, chunk_overlap=40)
        vectorstore = vectorstore.get_vectorstore(docs)
        retriever = vectorstore.as_retriever()
    except Exception as e:
        logging.error(f"Failed to create vectorstore: {e}")
        return
    
    if args.obfuscation_style == 'blank':
        correction_template = correction_template_blank
        correction_prompt = correction_prompt_blank
    else:
        correction_template = correction_template_random
        correction_prompt = correction_prompt_random
    
    logging.info(f"Obfuscating {lang} glosses...")
    obfuscator = GlossObfuscator(args.obfuscation_percentage, input_file='./sources/input.txt', obfuscation_style=args.obfuscation_style)  # 40% obfuscation
    obfuscator.obfuscate_file(output_file_path = './sources/obfuscated.txt')
    
    logging.info("Creating RAG chain...")
    logging.info(f"Template: {correction_template}")
    llm = ChatAnthropic(model=args.model)

    rag_chain_creator = RagChainCreator(retriever, llm)
    rag_chain = rag_chain_creator.create_rag_chain(correction_template)
    
    logging.info("Processing obfuscated file...")
    obfuscated_docs = process_file('./sources/obfuscated.txt')

    logging.info(f"Obfuscated files: {obfuscated_docs}")

    rag_out = []
    
    for doc in obfuscated_docs:
        llm_correction = rag_chain.invoke(f"""{correction_prompt}:
                                          
                            \\t {doc['text']}
                            \\m {doc['morphemes']}
                            \\g {doc['gloss']}

                              
                            """)
        retrieved_text = rag_chain_creator.get_relevant_docs(doc['text'] + ' ' + doc['morphemes'] + ' ' + doc['gloss'])
        page_content = list()
        metadata = list()
        for doc in retrieved_text:
            page_content.append(doc.page_content)
            metadata.append(doc.metadata)
        
        rag_out.append({'correction': llm_correction, 'retrieved_text': page_content, 'retreived_metadata': metadata})
    
    logging.info("Writing results to model_out.txt...")
    original_file = process_file('./sources/input.txt')
    print(original_file[0:2])

    with open(f'./outputs/model_out_{lang}.txt', 'w', encoding='utf-8') as f:
        for i,out in enumerate(rag_out):
            f.write(f"Original text: {original_file[i]['text']} \n\n")
            f.write(f"Model output (or obfuscated gloss): {obfuscated_docs[i]['gloss']} \n")
            f.write(f"Expected Gloss:{original_file[i]['gloss']} \n Translation: {original_file[i]['translation']} \n\n")

            formatted_output = json.dumps(out['correction'], indent=2).replace("\\n", "\n")
            f.write(formatted_output)
            
            f.write('-'*50 + '\n')
            for i, page in enumerate(out['retreived_metadata']):
                f.write(f"Retrieved metadata: {page} \n")
                f.write(f"Retrieved text: \n {out['retrieved_text'][i]} \n")
                f.write('-'*50)
            f.write('-'*50 + '\n' + 'x'*50 + '\n')
            f.write('\n')
    logging.info("Processing complete. Results written to model_out.txt")

if __name__ == "__main__":
    main()