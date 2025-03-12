map_prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                template="You are an expert signals intelligence analyst",
                input_variables=[],
            )
        ),
        HumanMessagePromptTemplate(
            prompt=PromptTemplate(
                template="As an intelligence analyst, review the chat transcripts below and write a one paragraph summary. Focus on the use of .onion domains for communication, language patterns, and the mix of Russian and English language. Also, analyze the informal chat text amidst onion email addresses. Cite specifics to support your analysis.\n\n---\n\n {text} \n\n---\n",
                input_variables=["text"],
            )
        ),
    ]
)

reduce_prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                template="You are an expert signals intelligence analyst.",
                input_variables=[],
            )
        ),
        HumanMessagePromptTemplate(
            prompt=PromptTemplate(
                template="Combine the intelligence briefs below into a unified brief on the targets's activity focusing on secure and anonymous communication infrastructure, language translation and cultural context understanding, and the identification of key entities/actors within the logs. If there is not enough context, make an informed estimation.\n\n---\n\n {text} \n\n---\n",
                input_variables=["text"],
            )
        ),
    ]
)