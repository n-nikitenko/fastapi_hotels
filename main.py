from fastapi import FastAPI, HTTPException
from fastapi.params import Body, Query

app = FastAPI()

hotels = [
    {"id": 1, "title": "Sochi", "stars": 3},
    {"id": 2, "title": "Dubai", "stars": 4},
]


@app.get("/hotels")
def get_hotels(hotel_id: int | None = Query(default=None), title: str | None = Query(default=None)):
    if hotel_id or title:
        return [hotel for hotel in hotels if hotel["id"]==hotel_id or hotel["title"]==title]
    return hotels


@app.delete("/hotels/{id}")
def remove_hotel(hotel_id: int):
    global hotels
    hotels = [hotel for hotel in hotels if hotel["id"]!=hotel_id]


@app.post("/hotels")
def create_hotel(title: str = Body(), stars: int = Body()):
    global hotels
    hotels.append({"id": len(hotels) + 1, "title": title, "stars": stars})
    return {"ok": True}


@app.put("/hotels/{hotel_id}")
def update_hotel(hotel_id: int, title: str = Body(), stars: int = Body()):
    global hotels
    hotel = next((hotel for hotel in hotels if hotel["id"]==hotel_id), None)
    if hotel:
        hotel.update({"title": title, "stars": stars})
        return {"ok": True}
    raise HTTPException(status_code=404, detail="Отель не найден")


@app.patch("/hotels/{hotel_id}")
def patch_hotel(hotel_id: int, title: str | None = Body(default=None), stars: int | None = Body(default=None)):
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
