map_prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                template="You are an expert incident responder",
                input_variables=[],
            )
        ),
        HumanMessagePromptTemplate(
            prompt=PromptTemplate(
                template="As an expert incident responder, review the dispatch call logs below and write a one paragraph summary. Focus on emergency situation details, geographical/location references, and references to potentially dangerous or illegal activities. Cite specifics to support your analysis.\n\n---\n\n {text} \n\n---\n",
                input_variables=["text"],
            )
        ),
    ]
)

reduce_prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                template="You are an expert incident responder.",
                input_variables=[],
            )
        ),
        HumanMessagePromptTemplate(
            prompt=PromptTemplate(
                template="Combine the incident response summaries below into a unified brief on the incident's activity with a focus on urgency or severity of reported incidents, verification of provided incident information, and coordination with relevant emergency service providers. If there is not enough context, make a best guess.\n\n---\n\n {text} \n\n---\n",
                input_variables=["text"],
            )
        ),
    ]
)