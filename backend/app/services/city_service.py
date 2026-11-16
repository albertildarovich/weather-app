from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import City


async def create_city(
    name: str,
    country: str | None,
    session: AsyncSession,
) -> City:

    city = City(
        name=name,
        country=country,
    )

    session.add(city)

    await session.commit()

    await session.refresh(city)

    return city

async def get_all_cities(session: AsyncSession) -> list[City]:
    statement = select(City).order_by(City.id)

    result = await session.execute(statement)

    cities = result.scalars().all()

    return list(cities)

async def get_city_by_id(
    city_id: int,
    session: AsyncSession,
) -> City | None:
    statement = select(City).where(City.id == city_id)

    result = await session.execute(statement)

    return result.scalar_one_or_none()