import asyncio

from app.db.database import AsyncSessionLocal
from app.services.city_service import get_all_cities


async def main():
    async with AsyncSessionLocal() as session:
        cities = await get_all_cities(session)

        if not cities:
            print("No cities found")
            return

        for city in cities:
            print(
                f"ID: {city.id} | "
                f"Name: {city.name} | "
                f"Country: {city.country}"
            )


if __name__ == "__main__":
    asyncio.run(main())