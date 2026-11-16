import asyncio

from app.db.database import AsyncSessionLocal
from app.services.city_service import create_city


async def main():
    async with AsyncSessionLocal() as session:
        city = await create_city(
            name="Berlin",
            country="Germany",
            session=session,
        )

        print(f"Created city: {city.name}")
        print(f"Country: {city.country}")
        print(f"ID: {city.id}")


if __name__ == "__main__":
    asyncio.run(main())