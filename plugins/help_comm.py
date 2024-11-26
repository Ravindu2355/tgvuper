from pyrogram import Client
from pyrogram import filters, types
from task_manager import process_tasks, start_task_processing


@Client.on_message(filters.command("start"))
async def _ms(client, message:types.Message):
    await message.reply("Hiiii")


@Client.on_message(filters.command("rerun"))
async def _rerun(client, message:types.Message):
  start_task_processing(client)
  await message.reply("started!")
