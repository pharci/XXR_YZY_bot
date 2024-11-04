import uvicorn
from multiprocessing import Process

def start_bot():
    import asyncio
    from bot.loader import main
    
    asyncio.run(main())

def start_admin():
    uvicorn.run("admin.api:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    bot_process = Process(target=start_bot)
    admin_process = Process(target=start_admin)

    bot_process.start()
    admin_process.start()

    bot_process.join()
    admin_process.join()