# Introduction

The system is not *general intellience*, *reasoning* or *autonomous decision-making*.

It is *statistical pattern recognition over text*, guided by *human feedback*.

Formally, this is a *supervised learning ranking problem over natural language inputs*, that is **Natural Language Processing (NLP)**.

Computers understand only numbers (in the form of bits). Hence, the greatest hurdle in the project would be how to assign a numerical value to text that preserve its meaning.

To do so, we convert the texts to vectors: embeddings. Looking for keywords only is insufficient due to synonyms, paraphrasing and implicit meaning. What we need is *semantic similarity*, not string matching.

An **embedding** is a fixed-length vector representation of text, learned from massive *corpora*, where semantic similarity corresponds to geometric proximity. This means that the vectors for words with similar meanings are positioned close to each other, and the distance and direction between the vectors encode the degree of similarity between the words. Mathematically, Text → ℝⁿ (e.g. ℝ⁷⁶⁸).

A **corpus** refers to a large and structured collection of text that is used for training, testing and evaluating NLP models. An example of a corpus would be all of Wikipedia. The process begins with *preprocessing the text* including *tokenization* and removing stopwords and punctuation. A *sliding context window* identifies target and context words, allowing the model to learn word relationships. Then, the model is trained to predict based on their context positioning semantically similar words close together in the vector space. Finally, throughout the training, the model parameters are adjusted to minimize prediction errors.

The **sliding context window** technique in NLP involves analyzing text by considering a subset or "window" of words sequentially. The window shifts through the text, enabling the model to capture context and semantic meaning effectively. For example, for the sentence: "I love chocolate but not cookies.", a sliding window context of size 3 will read: 

- I love chocolate
- but not cookies

## Signal vs Noise in Emails

When feeding emails in the model, we must make sure to extract maximum meaning in the minimum number of words possible. Long emails hurt. We will try to create a function that outputs one clean string per email.

One way to reduce noise is through *text normalization*. **Text normalization** is everything you do to make a messy text consistent and machine-learning friendly before modelling. Some typical steps are:

- Lowercasing: "FREE Offer" -> "free offer"
- Unicode normalization: smart quotes, weird hyphens, emojis -> consistent forms
- Punctuation handling: remove, keep or seperate (model-dependent)
- Stopword handling: optionally remove ('the', 'and', 'of', etc...)
- Stemming/lemmatization: "running", "ran" -> "run"
- Email-specific cleanup: 
    * Strip signatures, disclaimers
    * Remove quoted replies
    * Normalize URLs and emails
    - Collapse repeated characters ("looove" -> "love")

Text normalization is important as it:

- Reduces vocabulary size
- Improves statistical reliability
- Prevents models from learning noise

## Truncation strategies (emails)

Truncation decides what text you keep when an email is longer than the model's input limit. This is unavoidable for :

- Transformers (token limits)
- Classical ML pipelines with max feature sizes

Some common strategies are:

1) Head truncation:
    * Keep start of the email
    * Works well when the intent is upfront (support requests, spam)

2) Tail truncation:
    * Keep the end
    * Useful when signatures and final requests matter

3) Head + Tail:
    * Keep the beginning and end, drop the middle
    * Often best for long threads

4) Sliding window / chunking:
    * Split email into chunks, score each, aggregate
    * More accurate, more expensive

5) Structure-aware truncation:
    * Always keep:
        * Subject
        * First N sentences
        * Last reply in thread
    * Drop quoted history and boilerplate first

Choosing the right type of truncation matters as:

- Truncation changes meaning
- Poor truncation silently kills performance
- Email threads are especially dangerous because older content dominates token count

## Subject vs body weighting

Subject vs body weighting controls how much influence the subject line has compared to the email body.

Subjects are important as they are:

- Short
- Highly Intentional
- Often contain labels ("Invoice", "Re:Interview", "URGENT")

The different ways to weigh them are:

   1) Explicit duplication 
      * Append subject twice or more before the body

   2) Feature weighting (classical ML)
      * TF-IDF with higher weights for subject tokens

   3) Seperate Encoders
      * Encode subject and body independently
      * Combine the embeddings (sum, concat, attention)

   4) Special Tokens
      * [SUBJECT] ... [BODY] ... to let the model learn importance

When subject matters more

   - Email classification (spam, routing, priority)
   - Intent detection
   - Triage systems

When body matters more
   - Sentiment
   - Summarization
   - Compliance / policy detection

## How are all of these connected?

In practice your model, never sees "the email". It sees:

> Normalized text -> selectively truncated -> implicitly or explicitly weighted

That representation determines performance more than model choice in many email NLP tasks.

# The Text Normalization Process

## The Prelude

Before doing text normalization for the emails, we must first do *email parsing* and HTML -> Plain text conversion (FORMAT normalization).

During **email parsing**, we seperate the:

- Headers
- Subject
- Plain-text body
- HTML body
- Attachments

Examples of tasks include:

- Decode base64 bodies
- Handle multipart emails
- Choose plain texts vs HTML
- Extract subject line correctly

This step produces structured fields such as the subject, body text and body html. It is an example of **data extraction**. Here is an example of email data after email parsing:

>   {
>      "id": "19af9be7bd1997b1",
>      "subject": "Test email 2 (Chill)",
>      "sender": "Udhay Ramdoss \u003Cudhay1royalist@gmail.com\u003E",
>      "receiver": "\"udhayramdoss@gmail.com\" \u003Cudhayramdoss@gmail.com\u003E",
>      "date": "Sun, 7 Dec 2025 20:56:29 +0400",
>      "body": "Hi Udhay\r\n\r\nThis is a very chill issue :)\r\n\r\nKind regards,\r\nUdhay Ramdoss\r\n"
>    }