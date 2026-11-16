import asyncio

from app.db.database import AsyncSessionLocal
from app.services.city_service import get_city_by_id


async def main():
    async with AsyncSessionLocal() as session:
        city = await get_city_by_id(1, session)

        if city is None:
            print("City not found")
        else:
            print(city.name, city.country)

if __name__ == "__main__":
    asyncio.run(main())