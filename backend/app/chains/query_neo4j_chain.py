from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.neo4j.query_service import Neo4jDatabaseInspector

examples = [
    {

    }
]


class Neo4jQueryChain:
    def __init__(self, llm: BaseLanguageModel, user_prompt_template, system_prompt=None, examples=[], ):
        self.examples = examples
        self.llm = llm
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt_template

    def format_prompt(self, text):
        relation = Neo4jDatabaseInspector.get_all_relationships()
        relation_string = ",".join(relation)

        messages = [SystemMessage(self.system_prompt)]
        for e in self.examples:
            user_string = self.user_prompt.format(**e['user'])
            messages.append(HumanMessage(user_string))
            messages.append(AIMessage(e['assistant']))
        messages.append(
            HumanMessage(self.user_prompt.format(query=text, relation_type=relation_string)))
        return messages

    def invoke(self, query):
        messages = self.format_prompt(query)
        data = self.llm.invoke(messages)
        return data.content


def create_neo4j_query_chain(llm: BaseLanguageModel):
    pass
