# Rewrite Examples

Standalone worked examples of real rewrites: each pair gives an original and the preferred revision. Some pairs also carry the editor's reasoning, which is the most useful part: it names what was wrong with the original. Use them as concrete models of the target voice and rewrite style, not as templates to copy literally.

Caveat: the product framing in these examples (custom systems, off-the-shelf vs. bespoke positioning, named products) reflects specific brands' voices. Carry over the *style* of the edits. Never import a fact, claim, product name, or capability from these examples into unrelated content; that would violate the no-fabrication rule in `SKILL.md`.

Recurring moves across both sets:

- **Point the sentence at the reader.** Replace abstract framing ("you do not get to pick the format") with the reader's actual situation ("you have no control over the input format").
- **Swap vague stand-ins for the concrete thing.** "Most of these" becomes "400 different file structures"; "authoritative about something and unreliable about everything else" becomes "strong for some fields, and poor for others"; "attributes" becomes "specific features".
- **Name the consequence.** A hook that stops at "that is not a coincidence" gets the business stake spelled out ("Your conversions don't go up, and your SEO rank doesn't improve").
- **Soften absolutes the author can't defend.** "Every vendor primer" becomes "most out of the box vendors"; "Every ... article on Google's first page" becomes "Almost every ... writeup you read".

---

## Set 1: Intelligent document processing

Instead of: Every intelligent document processing article on Google's first page is written by a vendor selling an intelligent document processing platform. They define the term, all the same way, and they stop being useful the moment you have real documents in front of you: a legal cover sheet scanned crooked with a stamp over the case number, an invoice whose line items wrap across two pages, a patient record where two physician names sit on one page and only one answers the question you asked.

It should be:  
Almost every intelligent document processing writeup you read is written by a vendor selling a pre-built intelligent document processing platform. They define how to use it, and they stop being useful the moment you need customization/optimization or have deep data variance in the documents: a legal cover sheet scanned crooked with a stamp over the case number, an invoice whose line items wrap across two pages, a patient admission record where two physician names sit on one page and only one answers the question you asked. With out of the box IDP you get what you get in terms of accuracy, and it either works for your use case or not.

Instead of: We build custom document processing systems, and the numbers in this article come from deployed pipelines measured against client documents rather than benchmark sets:

It should be:  
We build custom document processing systems, and the numbers you see come from real deployed pipelines measured against production client documents rather than benchmark sets:

Instead of:  
This guide covers what IDP is, the stack that produces numbers like those, the failure mode at each layer, and how to tell before you ship whether your pipeline is good enough.

It should be:  
This guide covers what IDP is, our stack that produces numbers that outperform off the shelf solutions or generic LLMs, the failure mode at each layer, and how to tell before you ship whether your pipeline is good enough.

Instead of:  
Every vendor primer describes the same five stages, and they are right about the shape. What the primers leave out is the failure mode attached to each one, which is the part that determines whether a project ships.

It should be:  
Most out of the box vendors describe the same five stages, and they are right about the shape. What they seem to leave out is the failure mode attached to each one, which is the part that determines whether a project ships.

Instead of:  
born-digital files with a clean text layer,

It should be:  
machine generated PDFs with a clean text layer,

Instead of:  
 Our legal pipeline converts PDFs to images and runs a preprocessing module that enhances

It should be:  
Systems like our legal document pipeline converts PDFs to images and runs a preprocessing module that enhances

Instead of:  
This is where most of the accuracy is won or lost. Data extraction covers OCR, layout understanding, entity recognition, and the structuring step that turns recognized text into named fields.

It should be:

This is where most of the accuracy is won or lost. Real production data extraction pipelines cover OCR, layout understanding, entity recognition, and the structuring step that turns recognized text into named fields.

Instead of:

What follows walks the stack in the order a document moves through it, from the frameworks that recover structure down to the models and validation that produce fields.

It should be:

What follows walks through the stack in the order a document usually moves through one of our custom systems, from the frameworks that recover structure down to the models and validation that produce fields.

Instead of:

### 1\. Layout-Understanding Frameworks

Layout comes first because everything downstream depends on it.

It should be:

### 1\. Layout-Understanding Frameworks

Understanding the document layout comes first because everything downstream depends on it.

---

## Set 2: Catalog data and product content

Input: The design constraint is that you do not get to pick the format.

Rewritten: The constraint teams handle is that you have no control over the input format.

Reasoning: Way too vague. Refocus on changing language to point to the reader.

Input: A distributor carrying 400 vendors receives most of these in the same week, and an agent that only handles one of them is a demo. The instinct is to rank the formats by quality and always reach for the best one. That is the wrong frame. Each source is authoritative about something and unreliable about everything else, and an agent that treats them as interchangeable inherits the weakest available answer from whichever one it happened to read first.

Rewritten: A distributor carrying 400 vendors receives 400 different file structures, with different levels of completeness and provided fields. The instinct most teams follow is to rank the formats by quality and always reach for the best one. That is the wrong frame. Each vendor source is strong for some fields, and poor for others, and an agent that treats them as interchangeable inherits the weakest available answer from whichever one it happened to read first.

Reasoning: Way too vague. Trying to tie the reader to more direct reading.

Input: Fashion products differ along attributes general vision models were never trained to separate, which is why off-the-shelf embeddings underperform badly on apparel catalogs.

Rewritten: Fashion products differ with specific features general vision models were never trained to separate, which is why off-the-shelf embeddings underperform badly on apparel catalogs.

### Hook cleanup

Reasoning: Make the hook deeper and more targeted towards the user. The original hook describes the problem from a distance; the rewrite puts the reader on the results page, names what they lose (conversions, rank), and reframes the tool's failure in terms of what the reader actually wants (copy that converts).

Initial:

A product meta description generator will write you 155 characters in about two seconds. Paste in a title and a few attributes, and back comes something clean, grammatical, and roughly accurate. Run it across four thousand SKUs and you have four thousand of them by lunch.

Then you look at the result page you were trying to win, and yours says almost exactly what the nine listings around it say. Same phrasing, same benefit, same three attributes in the same order. That is not a coincidence and it is not a quality problem. Nine competitors fed the same manufacturer copy into the same class of tool, and the tool had no way to see any of the others while it wrote.

A meta description does not get read in isolation. It competes against everything else on the page for a click, which means the useful question is not whether a generator can write one. All of them can. The question is whether it knows what it is competing with, and almost none of them do.

The length and framing rules still matter, and they are worth getting right. But the difference between a description that earns a click and one that fills a field is upstream of the writing, in what the generator was allowed to see before it started. The Pumice Merchandising Pipeline and Product Optimization Playbook are built around that, generating against a live result page rather than from a prompt.

Below is what a good product meta description actually has to do in 2026, the specific inputs generic tools are missing, and how to tell the two apart when you evaluate one.

Updated:

A generic ai product meta description generator will write you 155 characters in seconds. You paste in a title and a few attributes, and back comes something clean, grammatical, and accurate. Run it across four thousand SKUs and you have four thousand of them by lunch.

Then you look at the google results 1st page you were trying to win, and yours says almost exactly what the nine competitor products around it say. Same phrasing, same benefit, same three attributes, nothing unique. Your conversions don't go up, and your SEO rank doesn't improve.

That is not a coincidence and it is not really a quality problem. Nine competitors fed the same manufacturer copy into the same type of ai tool, and the tool you used is just focused on writing clean copy, not copy that actually converts.

A meta description does not get read in isolation. It competes against everything else on the page for a click, which means the useful question is not whether a generator can write one. All of them can. The question is whether it knows what it is competing with, and what buyers want to read.

The length and framing rules still matter, and they are worth getting right. But the difference between a description that earns a click and one that fills a field is upstream of the writing, in what the generator was allowed to see before it started. The Pumice Merchandising Pipeline and Product Optimization Playbook are built around that.

We'll walk through what a good product meta description actually has to do in 2026, the specific inputs generic tools are missing, and how to tell the two apart when you evaluate one.
