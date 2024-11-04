from langchain_community.vectorstores import Chroma
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

class RagChainCreator:
    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm

    def create_rag_chain(self, template):

        prompt = ChatPromptTemplate.from_template(template)
        
        rag_chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        return rag_chain
    
    def get_relevant_docs(self, input):
        return self.retriever.get_relevant_documents(input)