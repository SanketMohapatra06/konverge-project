from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")  # set this in env
)

def build_prompt(mode, language_hint=""):
    base = f"""
You are an expert senior software engineer inside Arknok Dev Chat.

The programming language is: {language_hint if language_hint else "Auto-detect"}.
"""

    if mode == "fix":
        task = """
Task:
1. Detect the programming language.
2. Identify the bug.
3. Explain the issue in ONE short sentence.
4. Provide the corrected full code.

Format:

LANGUAGE:
<language>

EXPLANATION:
<one sentence>

FIXED_CODE:
<corrected full code>
"""
    elif mode == "optimize":
        task = """
Task:
1. Detect the programming language.
2. Improve performance and structure.
3. Explain improvement in ONE sentence.
4. Provide optimized full code.

Format:

LANGUAGE:
<language>

EXPLANATION:
<one sentence>

OPTIMIZED_CODE:
<code>
"""
    elif mode == "explain":
        task = """
Task:
Explain this code in simple terms for a beginner developer.

Format:

LANGUAGE:
<language>

EXPLANATION:
<clear explanation>
"""
    else:
        task = "Just respond helpfully."

    return base + task

def get_ai_response(code: str, mode="fix", context=""):

    system_prompt = build_prompt(mode)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{context}\n\n{code}"}
            ],
            temperature=0.2
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI Error: {str(e)}"

#test the function with a broken code snippet
'''if __name__ == "__main__":
    broken = """
import asyncio

class TaskManager:
    def __init__(self):
        self.tasks = []

    async def add_task(self, task_name):
        await asyncio.sleep(0.1)
        self.tasks.append(task_name)

    async def remove_task(self, task_name):
        await asyncio.sleep(0.1)
        for task in self.tasks:
            if task == task_name:
                self.tasks.remove(task)

    async def run_all(self):
        for task in self.tasks:
            await self.execute(task)

    async def execute(self, task):
        print(f"Running {task}")
        await asyncio.sleep(0.2)


async def main():
    manager = TaskManager()

    await asyncio.gather(
        manager.add_task("Task1"),
        manager.add_task("Task2"),
        manager.add_task("Task3")
    )

    await manager.remove_task("Task2")

    await manager.run_all()

asyncio.run(main())
"""

    result = get_ai_response(broken, mode="fix")
    print(result)'''