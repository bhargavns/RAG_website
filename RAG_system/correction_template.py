correction_template_blank = """
 \\t is a line in Arapaho (or some other low-resource language) and the second line (\\g) is the gloss in English/Spanish. \\m is the segmented morpheme line.
    Given a new example, your job is to correct the gloss line based on the provided grammar context.
    The grammar may not have all the answers, but you will need to see if it can inform the gloss correction.
    Remember to produce the output in exactly the same format as seen in the example below.
    You can also use your knowledge of English to correct some words where necessary. Missing words are indicated
    with a question mark (?). Replace all the '?' with their correct equivalents.

    Context:
    {context}

    Gloss to correct: {question}

    Output the result in the following JSON format:
    {{
        "gloss": "corrected gloss line",
        "explanation": "Detailed explanation of each word or morpheme",
        "how RAG was used": "Explanation of how the grammar document was used"
    }}

    Here is an example output that should be followed:

                              {{
                                "gloss": "\g one-time(0.8) A2S-enter(0.9) PREP(0.8) house(0.9)",
                                "explanation": "This sentence consists of four words:\\n
                                - 'juntiir' seems to be a compound of 'jun' (one) and 'tiir' (possibly related to time or occurrence). It's glossed as 'one-time', meaning 'once' or 'all at once'. (confidence: 0.8)\\n
                                - 'at'ok' can be broken down as: 'a-' (2nd person singular absolutive prefix, A2S), 't'ok' (verb root meaning 'to enter'). (confidence: 0.9)\\n
                                - 'laq' is a preposition (PREP) that likely means 'in' or 'into'. (confidence: 0.8)\\n
                                - 'jaa' is a noun meaning 'house' or 'home'. (confidence: 0.9)\\n
                                So the whole sentence 'juntiir at'ok laq jaa' can be glossed as 'one-time A2S-enter PREP house', which means something like 'You enter the house at once' or 'All at once, you go into the house'.",
                                "how RAG was used": "To generate this explanation, I used the following parts of the given Uspanteko grammar document:\\n
                                - The 'Marcadores de persona' (Person markers) section to identify the 2nd person singular absolutive prefix 'a-'.\\n
                                - The example sentences that used 'jun' for 'one' and compounds with 'tiir', though the exact meaning of 'juntiir' is inferred.\\n
                                - The preposition 'laq' which appeared in previous sentences, though its exact meaning is inferred from context.\\n
                                - The noun 'jaa' meaning 'house', which appeared in one of the example sentences.\\n

                                Confidence scores were assigned based on how closely each word or morpheme matched information provided in the grammar document. Higher scores (closer to 1.0) indicate a strong direct match, while lower scores (closer to 0.5) indicate a more tentative match based on context or inference. The lower confidence for 'juntiir' and 'laq' reflects the fact that their exact meanings are inferred rather than explicitly stated in the document."
                              }}

        
"""

correction_template_random = """
 \\t is a line in Arapaho (or some other low-resource language) and the second line (\\g) is the gloss in English/Spanish. \\m is the segmented morpheme line.
    Given a new example, your job is to correct the gloss line based on the provided grammar context.
    The grammar may not have all the answers, but you will need to see if it can inform the gloss correction.
    Remember to produce the output in exactly the same format as seen in the example below.
    You can also use your knowledge of English or Spanish to correct some words where necessary.

    If the gloss is in Spanish, maintain the Spanish gloss. If the gloss is in English, maintain the English gloss.

    If you are unsure about a morpheme, replace the label with a question mark (?) and also provide a context-based guess for the morpheme. 

    Context:
    {context}

    Gloss to correct: {question}
 
    Output the result in the following format:
        gloss: <corrected gloss line>,
        explanation: <Detailed explanation of each word or morpheme>,
        how RAG was used: <Explanation of how the grammar document was used>

    Here is an example output that should be followed:

                                gloss: one-time(0.8) A2S-enter(0.9) PREP(0.8) house(0.9),
                                explanation: This sentence consists of four words:\\n
                                - 'juntiir' seems to be a compound of 'jun' (one) and 'tiir' (possibly related to time or occurrence). It's glossed as 'one-time', meaning 'once' or 'all at once'. (confidence: 0.8)\\n
                                - 'at'ok' can be broken down as: 'a-' (2nd person singular absolutive prefix, A2S), 't'ok' (verb root meaning 'to enter'). (confidence: 0.9)\\n
                                - 'laq' is a preposition (PREP) that likely means 'in' or 'into'. (confidence: 0.8)\\n
                                - 'jaa' is a noun meaning 'house' or 'home'. (confidence: 0.9)\\n
                                So the whole sentence 'juntiir at'ok laq jaa' can be glossed as 'one-time A2S-enter PREP house', which means something like 'You enter the house at once' or 'All at once, you go into the house'.",
                                how RAG was used: To generate this explanation, I used the following parts of the given Uspanteko grammar document:\\n
                                - The 'Marcadores de persona' (Person markers) section to identify the 2nd person singular absolutive prefix 'a-'.\\n
                                - The example sentences that used 'jun' for 'one' and compounds with 'tiir', though the exact meaning of 'juntiir' is inferred.\\n
                                - The preposition 'laq' which appeared in previous sentences, though its exact meaning is inferred from context.\\n
                                - The noun 'jaa' meaning 'house', which appeared in one of the example sentences.\\n

                                Confidence scores were assigned based on how closely each word or morpheme matched information provided in the grammar document. Higher scores (closer to 1.0) indicate a strong direct match, while lower scores (closer to 0.5) indicate a more tentative match based on context or inference. The lower confidence for 'juntiir' and 'laq' reflects the fact that their exact meanings are inferred rather than explicitly stated in the document.

"""

correction_prompt_blank = """
Consider these 3 lines and correct the \\g line based on your understanding.
                            Make sure to replace all the ('?') with their correct equivalents.
                            DO NOT MISS ANY '?':
"""

correction_prompt_random = """
Consider these 3 lines and correct the \\g line based on your understanding.
                            Make sure to replace all the labels that you think are wrong with a ('?'). Then replace all the '?' with the correct morpheme label based on the retrieved grammar document.
                            DO NOT MISS ANY '?':
"""