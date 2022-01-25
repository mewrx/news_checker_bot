from os import getenv


chat_id = getenv("ADMIN_ID")

def is_admin(fn):
    """Decorator for admin check"""
    async def wrapper(arg):
        if chat_id == str(arg.from_user.id):
            await fn(arg)
    return wrapper