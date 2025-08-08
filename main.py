from fastapi import FastAPI, HTTPException
from fastapi.params import Body, Query

app = FastAPI()

hotels = [
    {"id": 1, "title": "Sochi", "name": "sochi"},
    {"id": 2, "title": "Дубай", "name": "dubai"},
    {"id": 3, "title": "Мальдивы", "name": "maldivi"},
    {"id": 4, "title": "Геленджик", "name": "gelendzhik"},
    {"id": 5, "title": "Москва", "name": "moscow"},
    {"id": 6, "title": "Казань", "name": "kazan"},
    {"id": 7, "title": "Санкт-Петербург", "name": "spb"},
]


@app.get("/hotels", tags=["Отели"])
async def get_hotels(
        hotel_id: int | None = Query(default=None),
        title: str | None = Query(default=None, description="Название отеля"),
        page: int |  None = Query(default=1, description="Номер страницы"),
        per_page: int | None = Query(default=5, description="Кол-во отелей на странице"),
):
    ret = hotels
    if hotel_id or title:
        ret = [hotel for hotel in hotels if hotel["id"]==hotel_id or hotel["title"]==title]
    start_idx = (abs(page) - 1) * abs(per_page)
    return ret[start_idx: start_idx + abs(per_page)]


@app.delete("/hotels/{id}")
async def remove_hotel(hotel_id: int):
    global hotels
    hotels = [hotel for hotel in hotels if hotel["id"]!=hotel_id]


@app.post("/hotels")
async def create_hotel(title: str = Body(), stars: int = Body()):
    global hotels
    hotels.append({"id": len(hotels) + 1, "title": title, "stars": stars})
    return {"ok": True}


@app.put("/hotels/{hotel_id}")
async def update_hotel(hotel_id: int, title: str = Body(), stars: int = Body()):
    global hotels
    hotel = next((hotel for hotel in hotels if hotel["id"]==hotel_id), None)
    if hotel:
        hotel.update({"title": title, "stars": stars})
        return {"ok": True}
    raise HTTPException(status_code=404, detail="Отель не найден")


@app.patch("/hotels/{hotel_id}")
async def patch_hotel(hotel_id: int, title: str | None = Body(default=None), stars: int | None = Body(default=None)):
    global hotels
    hotel = next((hotel for hotel in hotels if hotel["id"]==hotel_id), None)
    if hotel:
        if title:
            hotel.update({"title": title})
        if stars:
            hotel.update({"stars": stars})
        return {"ok": True}
    raise HTTPException(status_code=404, detail="Отель не найден")


if __name__=="__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        reload=True
    )
