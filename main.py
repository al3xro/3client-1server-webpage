
#FastAPI: Gestionare backend.
#Jinja2: Randează HTML.
#WebSocket: Comunicare real-time.
#Pydantic: Validare JSON.

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request

#FastAPI: Framework pentru construirea aplicațiilor web rapide și scalabile.
#WebSocket: Permite comunicarea bidirecțională între server și client (real-time).
#WebSocketDisconnect: Excepție care se declanșează când o conexiune WebSocket se închide.
#Request: Obiect folosit pentru a accesa informațiile despre o cerere HTTP.

from fastapi.responses import HTMLResponse

#HTMLResponse: Răspuns specializat pentru returnarea conținutului HTML.

from fastapi.templating import Jinja2Templates

#Creăm o instanță a clasei Jinja2Templates, care va căuta fișierele template HTML în directorul templates.
#Acest director trebuie să conțină fișiere HTML care vor fi completate cu datele din aplicația ta (ex: variabile ca temperatura, umiditate etc.).

from fastapi.middleware.cors import CORSMiddleware

#Aceasta înseamnă că importăm funcționalitatea CORS middleware din modulul middleware al FastAPI.
#FastAPI folosește middleware pentru a aplica funcționalități suplimentare între cererile HTTP și răspunsurile generate de server.

#import CORSMiddleware

#CORSMiddleware este un middleware care gestionează CORS (Cross-Origin Resource Sharing),
#o politică de securitate care controlează accesul la resursele serverului de pe un alt domeniu.

from pydantic import BaseModel

#UpdateData este un model definit de utilizator care moștenește de la BaseModel.
#Această clasă definește patru câmpuri: id (de tip str), temperature (de tip float), humidity (de tip float) și timestamp (de tip str).
#Pydantic va valida automat că datele trimise printr-o cerere POST care corespund acestui model au valorile corecte și de tipul corect. Dacă nu, va genera o eroare.

app = FastAPI() #Creăm instanța principală a aplicației FastAPI.

# Configure Jinja2 for HTML templates
templates = Jinja2Templates(directory="templates") #Specificăm locația fișierelor HTML pentru redare.

# Allow cross-origin requests
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
#Permitem accesul la API din orice sursă (important pentru frontend-backend).

# Static data to simulate temperature, humidity, and ID
data = {
    "id": "",
    "temperature": 0,
    "humidity": 0,
    "timestamp": ""
}
#Variabilă globală pentru stocarea valorilor curente de ID, temperatură, umiditate și timestamp.


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket): # Acceptă conexiuni noi
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket): # Închide conexiuni
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict): # Trimite mesaje tuturor clienților activi
        """Sends the latest data to all connected WebSocket clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                self.disconnect(connection)
#Clasă care gestionează conexiunile WebSocket (real-time).

manager = ConnectionManager()
#Prin crearea unei instanțe a ConnectionManager și atribuirea acesteia variabilei manager,
#devine posibilă gestionarea eficientă a tuturor conexiunilor WebSocket active în aplicație
#și trimiterea de actualizări în timp real către fiecare client conectat.

# Pydantic model for JSON payload
class UpdateData(BaseModel): #Definește structura datelor primite pentru actualizare (id, temperatură, umiditate, timestamp).
    id: str  # Adăugăm câmpul ID
    temperature: float
    humidity: float
    timestamp: str


@app.get("/", response_class=HTMLResponse) #Dashboard HTML, Returnează un fișier HTML pentru vizualizarea datelor.
async def get_dashboard(request: Request):
    """Serves the HTML dashboard."""
    return templates.TemplateResponse("dashboard.html", {"request": request, "data": data})


@app.post("/update") #Endpoint POST pentru actualizare. Actualizează datele globale și notifică clienții WebSocket.
async def update_data(payload: UpdateData):
    """Updates ID, temperature, humidity, and timestamp using JSON payload."""
    data["id"] = payload.id  # Actualizăm ID-ul
    data["temperature"] = payload.temperature
    data["humidity"] = payload.humidity
    data["timestamp"] = payload.timestamp
    # Notify WebSocket clients
    await manager.broadcast(data)
    return {"status": "success", "updated_data": data}


@app.websocket("/ws") #Endpoint WebSocket pentru real-time. Gestionează conexiunile WebSocket și comunicarea bidirecțională.
async def websocket_endpoint(websocket: WebSocket):
    """Handles WebSocket connections for real-time updates."""
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

#Pornirea serverului se face in terminal cu comanda:  uvicorn main:app --reload
