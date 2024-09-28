import logging
import json

import asyncpg
import chainlit as cl
import rag
from config import POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER
from pgvector.asyncpg import register_vector

logger = logging.getLogger(__name__)


async def init_db():
    conn = await asyncpg.connect(
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database=POSTGRES_DB,
    )
    await register_vector(conn)
    return conn

@cl.step(type="tool")
async def tool():
    # Fake tool
    await cl.sleep(2)
    return "Response from the tool!"


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Recreate index",
            message="/reindex",
        )
    ]

@cl.action_callback("reindex")
async def on_action(action: cl.Action):
    logger.info(f"Received action: {action.value}")
    final_answer = await cl.Message(content=f"Executing {action.value}").send()
    
    conn = await init_db()
    try:
        await rag.reindex_dataset(conn)
    finally:
        await conn.close()

    final_answer.content = f"Executing {action.value}: Done!"
    await final_answer.update()
    action.value = "reindex_done"


@cl.on_message  # this function will be called every time a user inputs a message in the UI
async def main(message: cl.Message):
    """
    This function is called every time a user inputs a message in the UI.
    It sends back an intermediate response from the tool, followed by the final answer.

    Args:
        message: The user's message.

    Returns:
        None.
    """
    logger.info(f"Received message: {message.content}")
    response = await cl.Message(content="").send()

    if message.content == "/reindex":
        actions = [
            cl.Action(label="Yes", name="reindex", value="reindex", description="Yes"),
        ]
        response.content = "Do you want to recreate the index?"
        response.actions = actions
    else:
        response.content = "Searching..."
        await response.update()
        conn = await init_db()
        try:
            results = await rag.search(conn, message.content)
            logger.info(f"Results: {results}")
            response.content = "\n".join([f"id: {result['id']} (score: {result['match_score']:.3f}): {result['content']}" for result in results])
        except Exception as e:
            logger.error(f"Error: {e}")
            response.content = f"Error: {e}"
        finally:
            await conn.close()

    await response.update()
