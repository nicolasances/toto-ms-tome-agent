# Tome Agents 

This microservice provides the agents backend for the Tome app. 

## Notes & Choices

 * LLMs are often **throttled**, so I've encountered some problems when **generating too many questions**, for examples when some topics have a very large amounts of sections. <br>
 An example is for a Topic of 25 sections, generating 4 questions per section in parallel was blocked by the LLM provider. <br>
 For that reason, I have to limit the length of a Topic Review. 