# RAG Story Project Notes

## Challenge 1: Why Can't You Just Paste the Whole Story In?

I tested giving the entire story directly to the model in the prompt and asking questions about it. Since the story is short, the model can answer questions because the whole story fits inside the context.

However, this approach would not work well for very large documents. A much longer story or a collection of documents could exceed the model's context limit, cost more because more text is sent every time, and make it harder for the model to focus on the exact information needed.

Retrieval is useful because instead of sending the entire document, we can find only the relevant parts and give those parts to the model.

---

## Challenge 2: Breaking the Story Into Searchable Pieces

I split the story into chunks based on paragraphs.

I chose paragraph-based chunking because each paragraph represents a complete event or idea in the story. Splitting by sentences could separate important context, while splitting randomly by character count could break the story in the middle of an event.

For this story, the splitting process created 11 chunks.

Example:

Chunk 3 contains the event where Elena hears a sound during the storm, finds Tomas in the water, and rescues him. Keeping this information together helps preserve the meaning of the scene.

I decided not to use overlap because the story paragraphs already contain enough context and the document is small. Overlap sometimes help with not breaking the context of the document, but since our story is splitted naturally no need for overlapping.

After creating the chunks, I stored them in a ChromaDB collection along with their embeddings. This allows the system to search through the stored vectors instead of manually comparing every chunk in memory.

## Challenge 3: Representing Meaning, Not Just Words


I learned that embeddings are numerical representations of text that capture the meaning and relationships between pieces of text. Instead of comparing text based only on matching words, embeddings allow the system to compare the semantic similarity between different texts.

The embedding process converts a piece of text into a vector, which is a list of numbers. These vectors can then be compared to measure how similar two pieces of text are.

In the RAG pipeline, each story chunk will be converted into an embedding and stored. When a user asks a question, the question will also be converted into an embedding. The system can then compare the question vector with the stored chunk vectors to identify the most relevant parts of the story.

I learned that embeddings are used for retrieval and similarity search, not for generating answers. After the relevant information is retrieved, the language model uses that information to generate the final response.

The embeddings API accepts text as input and returns a numerical vector representing the meaning of that text.

The similarity between embeddings is measured using cosine similarity. It compares the direction of two vectors to determine how close their meanings are. A score closer to 1 means the texts are more semantically similar, while a score closer to 0 means they are less related. Embeddings from different models cannot be compared. Embeddings need to be stored with the original text to be able to know what text belongs to it. Embedding model doesn't know the answer it only create the vector that helps find related information. It has a fixed size and the position of the number doesn't have human meaning. 
Experiment:

Input:
A story chunk about Tomas Rigg surviving the shipwreck.

Model:
text-embedding-3-small

Output:
A vector containing 1536 numbers.

The returned vector represents the semantic meaning of the text, which can be compared with other vectors to find similar content.

The embeddings were generated using the text-embedding-3-small model and stored inside ChromaDB together with the original story chunks. The database keeps the relationship between the text and its vector representation, allowing the retrieval system to find similar meanings later.

## Challenge 4: Finding the Right Piece

I created a retrieval system using ChromaDB vector search. ChromaDB compares the question embedding with stored story embeddings and returns the chunks with the highest similarity.

Process:

1. Convert every story chunk into an embedding.
2. Store the embeddings and chunks inside ChromaDB.
3. Convert the user's question into an embedding.
4. Send the question embedding to ChromaDB.
5. ChromaDB searches for the most similar stored embeddings.
6. The highest scoring chunks are returned as context.

Instead of manually calculating similarity between every chunk using cosine similarity, the vector database handles the similarity search operation and returns the most relevant documents.
Example question:

"Who survived the shipwreck?"

Retrieved chunk:

Chunk 4

Reason:

The chunk contains the sentence:
"Tomas Rigg, twenty-nine years old, the last survivor of a four-person crew aboard a fishing boat called the Kestrel Anne."

The similarity score was highest because the meaning of the question matched the content of this chunk.

## Challenge 5: Wiring It Into the LLM

I connected the retrieval system to the language model using a tool called `search_story`.

The tool accepts:

- A natural language question from the user.

The tool returns:

- The most relevant chunks from the story based on embedding similarity.

The flow of the system:

1. The user asks a question about the story.
2. The model is provided with the search_story tool and is instructed to use it before answering questions. When the tool is called, my code performs the retrieval and returns relevant story chunks.
3. The question is converted into an embedding.
4. The question embedding is sent to ChromaDB, which compares it with the stored story chunk embeddings and returns the most relevant chunks.
5. The most relevant chunks are retrieved.
6. The retrieved chunks are provided to the model as context.
7. The model generates an answer using only the retrieved story information.

Example:

Question:

"Who survived the shipwreck?"

Retrieved information:

The chunk explaining that Tomas Rigg was the last survivor of the Kestrel Anne shipwreck.

Answer:

"Tomas Rigg was the last survivor of the shipwreck aboard the fishing boat called the Kestrel Anne."

The system was also tested with a question that was not in the story:

Question:

"What is the capital of France?"

Answer:

"I don't know."

This showed that the model was using the provided story context instead of answering from its general knowledge.

## Stretch Challenge: Multi-chunk Retrieval

Question:

"How did Tomas get Henrik's compass?"

Result:

The system correctly combined information from multiple parts of the story.

Relevant chunks:

- Chunk 5: The compass was the same type that belonged to Elena's grandfather Henrik Voss.
- Chunk 6: Tomas received the compass from his father Mattias Holt.
- Chunk 7: Henrik gave the compass to Mattias when he rescued him.

Observation:

This question could not be answered completely from one chunk. The retrieval system needed multiple chunks to reconstruct the full history of the compass.

## Using a Vector Database (ChromaDB)

I used ChromaDB as the vector database for storing and searching story information.

The database stores:
- The original story chunks.
- Their embeddings.
- Unique IDs for each chunk.

When a user asks a question:
1. The question is converted into an embedding.
2. ChromaDB compares it with stored embeddings.
3. The closest chunks are returned.
4. These chunks are passed to the LLM as context.

A normal database like MySQL stores structured data using rows and columns, but it is not designed for semantic similarity search. A vector database is better for RAG because it can search based on meaning rather than exact keyword matches.

## Unknown Question Test

Question:

"What is the capital of France?"

Result:

"I don't know."

Observation:

The system correctly refused to answer because the information was not present in the retrieved story chunks. This prevents the model from using outside knowledge and reduces hallucination.