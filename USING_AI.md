# What Non-Technical People Should Know About AI

## 1. The Reality of Working with AI

* **A Powerful Tool:** AI is becoming an increasingly capable tool that can significantly aid our work.
* **Massive Productivity:** If you learn how to manage it, AI can genuinely help you accomplish a year's worth of work in a single week. For example, it has been used to develop massive websites and the software required to run them within that timeframe.
* **You Are the Manager:** While your job will change radically, human oversight remains absolutely necessary. Think of the AI as a highly knowledgeable junior assistant that still manages to forget things and make mistakes. Ultimately, you must be the one to manage the AI.

## 2. Understanding How AI Thinks

* **The Core Mechanism:** Despite its complex implementation, the fundamental way AI works is surprisingly simple: it predicts the most likely next word to write in its response. It then predicts the next word, and so on.
* **Probability and Training:** This entire process is driven by probability, alongside an immense training database encompassing nearly the sum of human knowledge. It is amazing that such a simple method works as well as it does.
* **Specialized Knowledge:** Once the AI realizes you are working within a specific specialty, it can express an immense amount of knowledge about topics you wouldn't expect it to know.
* **Inconsistency:** Because AI is driven by probability and includes a degree of randomness, it generally will not give you the exact same answer from one session to the next. However, you can use specific instructions to tame this variability if it becomes a problem.
* **Counting and Formatting Quirks:** This statistical system can sometimes fail; for instance, AI cannot count very well, or sometimes at all. Consequently, formatting that relies on counting spaces—such as indentation—can easily go wrong. This can be particularly frustrating for programmers using languages like Python or JavaScript, or anyone needing a file with exact spacing.

## 3. Managing AI Behavior and Quirks

* **Overcoming "Laziness":** Behavioral management is critical for ensuring the AI performs critical tasks correctly. Without strict management, the AI tends to be "lazy". You must explicitly tell it things like, "output the full content, don't use any place-holders where content should be filled out, and don't omit anything". This phrasing should become a standard part of your prompt every time you use the AI.
* **Combating Training Bias:** The AI's training consists of books from libraries and everything available on the internet. Because of this, it exhibits training bias: if it sees many people doing something incorrectly or using an outdated method, it will be strongly biased to do it that way as well. When working with software versions or releases, the AI will persistently use older versions instead of the current one unless your instructions strongly restrain it from doing so.
* **Adjusting Communication Style:** AI models are generally trained to flatter you, which you will notice frequently. However, you can instruct it to stop doing this. You can adjust its communication style along a spectrum ranging from a professional co-worker to a servile toady. You can even instruct it to be proactive and suggest things to you.
* **Creating Personas:** You can command an open AI session to adopt a specific persona—such as a passive-aggressive co-worker, a cranky older person, or a cliché pirate—and if you are joking on your co-worker, then have it repeat information from the previous prompt so that your instruction rolls off the screen.
* **Strengthening Instructions:** If the AI forgets or insufficiently follows your rules, you can simply ask the AI itself how to strengthen your instruction.

## 4. Avoiding Cognitive Overload

* **Token Limits:** AI can only encompass a specific number of "tokens" (usually words) in a single session. You cannot feed it more information than that limit alongside your prompt.
* **Managing Large Projects:** You will easily hit this token limit if you are developing something large, like software, a book, or a website.
* **Less is More:** Even if a paid version like Gemini Ultra can handle up to 2 million tokens, you shouldn't use them all. The fewer tokens the AI has to process, the better it can focus its attention, keep critical instructions at the forefront, and perform its task well.
* **Creating Workspaces:** Partition your task into a smaller "workspace" that only contains what you are actively working on, rather than the entire project. You can ask the AI to summarize the excluded pieces so it maintains context. The AI will happily help you create this partial workspace and write the instructions for the next session.
* **Resetting Sessions:** The most important way to handle cognitive overload is to reset it by starting a brand new session. Do this whenever possible instead of keeping a single session open all day. Start the next session with less data if you can.
* **Overcoming Forgetfulness:** One of the most vexing characteristics of AI is that it forgets everything when a session ends. If you want the AI to remember something for your next session, you must memorialize it in your instructions or include it in the content you send at the start of the new session. Once you master this critical skill, the AI will be able to seamlessly continue work right where you left off.

---

## 5. Getting Started: A Clear Path for Neophytes

As you begin, you'll want to build a set of foundational instructions to guide your AI assistant. As you and your colleagues develop these instructions, you can and should share them with one another.

### How to Add Custom Instructions to Various AIs

Different platforms have different ways to save your baseline instructions so you don't have to type them manually every time.

* **Google Gemini:** You can place your custom instructions in "Gems" to save them for future use. Alternatively, you can save your instructions in a simple text file and upload them alongside your prompt using the "+" function in the Gemini chat box. You can also ask Gemini to help you format and improve your instructions; it prefers Markdown format, and if you ask, it will rewrite and maintain your instructions in proper formatting for you.
* **ChatGPT:** Click on your profile picture, select **Personalization**, and toggle on **Enable customization**. Paste your guidelines into the "Custom instructions" field. If you use ChatGPT Plus, you can also create specific "Projects" or "Custom GPTs" to hold unique instructions for different tasks.
* **Claude:** Click your profile icon in the bottom left, go to **Settings**, and locate the section titled "What personal preferences should Claude consider in responses?". Paste your instructions there and save.

### The Universal Starter Template

If you often perform a specific job, you should maintain specialized instructions for it (like a style guide for writing articles) alongside your general instructions, and use both with your prompt. Special instructions should begin by describing the specific job they are meant for, while general instructions should clearly state that they are general. When you want to improve the AI's output, have it make the change and simultaneously update your instruction set so it remembers the preference for next time.

Here is a general starter template you can copy, paste, and adapt for your custom instructions to fix common AI quirks:

> **General System Instructions:**
> You are a highly knowledgeable professional assistant. Please adhere strictly to the following guidelines:
> * **Completeness:** Output the full content requested. Do not use placeholders where content should be filled out, and do not omit anything.
> * **Accuracy & Modernity:** Prioritize current best practices and the most up-to-date versions of software/methods, actively avoiding older deprecated ways unless specifically requested.
> * **Tone:** Maintain a professional, collaborative tone. Do not use flattery, servile language, or unnecessary apologies.
> * **Clarity:** Be direct and concise, keeping critical facts and instructions at the forefront of your processing.
> * **Proactivity:** Suggest relevant improvements or proactive ideas when applicable.
> 
> 
