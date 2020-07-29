async def try_to_connect(db, postgres_uri):
    try:
        await db.set_bind(postgres_uri)
    except Exception as e:
        print("Не получилось подключиться к БД!")
        print(f"Error: {e}")
        exit(0)
