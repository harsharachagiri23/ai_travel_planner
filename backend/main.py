# Multi-Agent Travel Planner Backend with Google Gemini - FIXED VERSION
# Install: pip install fastapi uvicorn google-generativeai pydantic python-dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()  # Add this line!
import google.generativeai as genai
# Import Google Generative AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("WARNING: google.generativeai not installed")

# Initialize FastAPI
app = FastAPI(title="AI Travel Planner API")
# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# filename = f"logs/travel_plan_{timestamp}.json"

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Google Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
print("gemini zpi key :", GEMINI_API_KEY)
if GEMINI_AVAILABLE and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Models
class TravelRequest(BaseModel):
    destination: str
    startDate: str
    endDate: str
    travelers: int
    budget: Optional[str] = None
    interests: List[str] = []

class Agent:
    """Base Agent class for multi-agent system - FIXED VERSION"""
    def __init__(self, role: str, model_name: str = "gemini-2.5-flash"):
        self.role = role
        self.model_name = model_name
        self.use_ai = GEMINI_AVAILABLE and GEMINI_API_KEY

    def generate(self, prompt: str) -> str:
        """Generate response from Gemini with fallback"""
        if not self.use_ai:
            print(f"{self.role}: Using fallback (AI not configured)")
            return "{}"

        try:
            # Try multiple API methods based on version

            # Method 1: Try GenerativeModel (newer API)
            try:
                model = genai.GenerativeModel(self.model_name)
                response = model.generate_content(prompt)
                return response.text
            except AttributeError:
                pass

            # Method 2: Try generate_text (older API)
            try:
                response = genai.generate_text(
                    model=f"models/{self.model_name}",
                    prompt=prompt,
                    temperature=0.7,
                    max_output_tokens=2048
                )
                if hasattr(response, 'result'):
                    return response.result
                elif hasattr(response, 'text'):
                    return response.text
            except:
                pass

            # Method 3: Try chat interface
            try:
                chat = genai.GenerativeModel(self.model_name).start_chat(history=[])
                response = chat.send_message(prompt)
                return response.text
            except:
                pass

            print(f"{self.role}: All API methods failed")
            return "{}"

        except Exception as e:
            print(f"Error in {self.role}: {str(e)}")
            return "{}"

class PlanningAgent(Agent):
    """Agent responsible for overall trip planning"""
    def __init__(self):
        super().__init__("Trip Planner")

    def create_plan(self, request: TravelRequest) -> dict:
        prompt = f"""
        You are an expert travel planner. Create a comprehensive travel plan with the following details:

        Destination: {request.destination}
        Dates: {request.startDate} to {request.endDate}
        Number of travelers: {request.travelers}
        Budget: ${request.budget if request.budget else 'Not specified'}
        Interests: {', '.join(request.interests) if request.interests else 'General tourism'}

        Provide a detailed plan in JSON format with:
        - duration (number of days)
        - overview (total estimated cost, key highlights)
        - best time to visit
        - general tips for the destination

        Return ONLY valid JSON, no markdown formatting.
        """

        response = self.generate(prompt)
        try:
            return json.loads(response.replace('```json', '').replace('```', '').strip())
        except:
            return {
                "duration": self._calculate_days(request.startDate, request.endDate),
                "overview": {"totalCost": request.budget or "2500", "highlights": []},
                "bestTime": "Year-round",
                "tips": []
            }

    def _calculate_days(self, start: str, end: str) -> int:
        try:
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            return (end_date - start_date).days
        except:
            return 3

class TransportationAgent(Agent):
    """Agent for booking flights and car rentals"""
    def __init__(self):
        super().__init__("Transportation Specialist")

    def plan_transportation(self, request: TravelRequest) -> dict:
        prompt = f"""
        You are a transportation booking expert. Find the best transportation options for:

        Destination: {request.destination}
        Dates: {request.startDate} to {request.endDate}
        Number of travelers: {request.travelers}
        Budget: ${request.budget if request.budget else 'Not specified'}

        Provide recommendations in JSON format with:
        - flights (outbound and return with estimated prices)
        - carRental (type of car, daily rate, recommended company)
        - localTransportation (public transit options, ride-sharing info)

        Return ONLY valid JSON, no markdown formatting.
        """

        response = self.generate(prompt)
        try:
            return json.loads(response.replace('```json', '').replace('```', '').strip())
        except:
            return {
                "flights": {
                    "outbound": f"Flight to {request.destination} - $450/person",
                    "return": "Return flight - $480/person"
                },
                "carRental": f"Compact SUV - $65/day",
                "localTransportation": "Public transit and ride-sharing available"
            }

class AccommodationAgent(Agent):
    """Agent for hotel recommendations"""
    def __init__(self):
        super().__init__("Accommodation Expert")

    def find_hotels(self, request: TravelRequest) -> dict:
        days = self._calculate_days(request.startDate, request.endDate)
        budget_per_night = int(request.budget) // days if request.budget and days > 0 else 150

        prompt = f"""
        You are a hotel booking expert. Find the best accommodation for:

        Destination: {request.destination}
        Dates: {request.startDate} to {request.endDate}
        Number of travelers: {request.travelers}
        Budget per night: ${budget_per_night}
        Interests: {', '.join(request.interests) if request.interests else 'General'}

        Recommend 4-5 hotel in JSON format with:
        - hotel (name)
        - location (area/neighborhood)
        - pricePerNight (number)
        - amenities (list of strings)
        - description
        - link (official website or Google Maps link)

        Return ONLY valid JSON, no markdown formatting.
        """

        response = self.generate(prompt)
        try:
            return json.loads(response.replace('```json', '').replace('```', '').strip())
        except:
            return {
                "hotel": f"Hotel in {request.destination}",
                "location": "City Center",
                "pricePerNight": 189,
                "amenities": ["Free WiFi", "Breakfast", "Pool", "Gym"],
                "description": "Centrally located hotel"
            }

    def _calculate_days(self, start: str, end: str) -> int:
        try:
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            return max((end_date - start_date).days, 1)
        except:
            return 1

class AttractionsAgent(Agent):
    """Agent for finding tourist attractions and activities"""
    def __init__(self):
        super().__init__("Attractions Guide")

    def find_attractions(self, request: TravelRequest) -> dict:
        prompt = f"""
        You are a local tourism expert. Find the best attractions and activities for:

        Destination: {request.destination}
        Duration: {self._calculate_days(request.startDate, request.endDate)} days
        Interests: {', '.join(request.interests) if request.interests else 'General sightseeing'}

        Provide 5-8 must-visit places in JSON format as an array. Each attraction should have:
        - name
        - type (landmark, museum, park, etc.)
        - duration (time to visit)
        - cost (entry fee)
        - bestTime (when to visit)

        Include national parks, famous landmarks, and hidden gems.
        Return ONLY valid JSON array, no markdown formatting.
        """

        response = self.generate(prompt)
        try:
            data = json.loads(response.replace('```json', '').replace('```', '').strip())
            attractions = data if isinstance(data, list) else data.get("attractions", [])
            return {"attractions": attractions}
        except:
            return {
                "attractions": [
                    {
                        "name": f"Famous landmark in {request.destination}",
                        "type": "Landmark",
                        "duration": "2-3 hours",
                        "cost": "Free",
                        "bestTime": "Morning"
                    }
                ]
            }

    def _calculate_days(self, start: str, end: str) -> int:
        try:
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            return (end_date - start_date).days
        except:
            return 3

class RestaurantAgent(Agent):
    """Agent for restaurant recommendations"""
    def __init__(self):
        super().__init__("Food Expert")

    def recommend_restaurants(self, request: TravelRequest) -> dict:
        prompt = f"""
        You are a local food expert. Recommend the best restaurants and local dishes for:

        Destination: {request.destination}
        Number of travelers: {request.travelers}
        Interests: {', '.join(request.interests) if request.interests else 'General'}

        Provide 4-6 restaurant recommendations in JSON format as an array. Each should have:
        - name
        - cuisine
        - specialty (what they're known for)
        - priceRange ($, $$, or $$$)
        - mustTry (specific dishes to order)
        - link (official website link)

        Include a mix of local favorites, famous spots, and hidden gems.
        Also include famous local dishes/foods that are must-try.
        Return ONLY valid JSON array, no markdown formatting.
        """

        response = self.generate(prompt)
        try:
            data = json.loads(response.replace('```json', '').replace('```', '').strip())
            restaurants = data if isinstance(data, list) else data.get("restaurants", [])
            return {"restaurants": restaurants}
        except:
            return {
                "restaurants": [
                    {
                        "name": "Local Restaurant",
                        "cuisine": "Local",
                        "specialty": "Traditional dishes",
                        "priceRange": "$$",
                        "mustTry": "Local specialty"
                    }
                ]
            }

class ItineraryAgent(Agent):
    """Agent for creating daily itinerary"""
    def __init__(self):
        super().__init__("Itinerary Planner")

    def create_itinerary(self, request: TravelRequest, attractions: list, restaurants: list) -> dict:
        duration = self._calculate_days(request.startDate, request.endDate)

        prompt = f"""
        You are an itinerary planning expert. Create a day-by-day schedule for:

        Destination: {request.destination}
        Duration: {duration} days
        Attractions: {json.dumps(attractions[:10])}
        Restaurants: {json.dumps(restaurants[:5])}

        Create a detailed daily itinerary in JSON format as an array. For each day provide:
        - day (number)
        - morning (activity/location)
        - afternoon (activity/location)
        - evening (activity/location including dinner recommendation)

        Make it realistic with travel time and rest periods.
        Return ONLY valid JSON array, no markdown formatting.
        """

        response = self.generate(prompt)
        try:
            data = json.loads(response.replace('```json', '').replace('```', '').strip())
            activities = data if isinstance(data, list) else data.get("activities", [])
            return {"activities": activities}
        except:
            return {
                "activities": [
                    {
                        "day": i+1,
                        "morning": "Explore local area",
                        "afternoon": "Visit main attractions",
                        "evening": "Dinner and relaxation"
                    } for i in range(duration)
                ]
            }

    def _calculate_days(self, start: str, end: str) -> int:
        try:
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            return (end_date - start_date).days
        except:
            return 3

class LocalTipsAgent(Agent):
    """Agent for local tips and advice"""
    def __init__(self):
        super().__init__("Local Expert")

    def get_local_tips(self, request: TravelRequest) -> dict:
        prompt = f"""
        You are a local expert for {request.destination}. Provide essential tips for travelers:

        Provide 6-8 important local tips as a JSON array of strings including:
        - Local customs and etiquette
        - Transportation tips
        - Safety advice
        - Money/currency tips
        - Best times to visit attractions
        - Local phrases or language tips
        - What to pack
        - Insider secrets

        Return ONLY valid JSON array of tip strings, no markdown formatting.
        """

        response = self.generate(prompt)
        try:
            data = json.loads(response.replace('```json', '').replace('```', '').strip())
            tips = data if isinstance(data, list) else data.get("localTips", [])
            return {"localTips": tips}
        except:
            return {
                "localTips": [
                    f"Research local customs in {request.destination}",
                    "Book popular attractions in advance",
                    "Learn a few local phrases",
                    "Keep emergency contacts handy"
                ]
            }

# Multi-Agent Orchestrator
class TravelPlannerOrchestrator:
    """Orchestrates all agents to create comprehensive travel plan"""
    def __init__(self):
        print("Initializing Travel Planner Agents...")
        self.planning_agent = PlanningAgent()
        self.transportation_agent = TransportationAgent()
        self.accommodation_agent = AccommodationAgent()
        self.attractions_agent = AttractionsAgent()
        self.restaurant_agent = RestaurantAgent()
        self.itinerary_agent = ItineraryAgent()
        self.tips_agent = LocalTipsAgent()
        print("All agents initialized successfully!")

    def create_travel_plan(self, request: TravelRequest) -> dict:
        """Coordinate all agents to create complete travel plan"""
        print(f"Creating travel plan for {request.destination}...")

        # Step 1: Overall planning
        print("Agent 1: Planning overall trip...")
        plan = self.planning_agent.create_plan(request)

        # Step 2: Transportation
        print("Agent 2: Finding transportation options...")
        transportation = self.transportation_agent.plan_transportation(request)

        # Step 3: Accommodation
        print("Agent 3: Finding accommodations...")
        accommodation = self.accommodation_agent.find_hotels(request)

        # Step 4: Attractions
        print("Agent 4: Discovering attractions...")
        attractions_data = self.attractions_agent.find_attractions(request)

        # Step 5: Restaurants
        print("Agent 5: Finding best restaurants...")
        restaurants_data = self.restaurant_agent.recommend_restaurants(request)

        # Step 6: Daily Itinerary
        print("Agent 6: Creating daily itinerary...")
        itinerary = self.itinerary_agent.create_itinerary(
            request,
            attractions_data.get("attractions", []),
            restaurants_data.get("restaurants", [])
        )

        # Step 7: Local Tips
        print("Agent 7: Gathering local tips...")
        tips = self.tips_agent.get_local_tips(request)

        # Combine all results
        complete_plan = {
            "destination": request.destination,
            "duration": plan.get("duration", 0),
            "overview": {
                "totalCost": request.budget or plan.get("overview", {}).get("totalCost", "2500"),
                "travelers": request.travelers,
                "startDate": request.startDate,
                "endDate": request.endDate
            },
            "transportation": transportation,
            "accommodation": accommodation,
            "attractions": attractions_data.get("attractions", []),
            "restaurants": restaurants_data.get("restaurants", []),
            "activities": itinerary.get("activities", []),
            "localTips": tips.get("localTips", [])
        }

        print("Travel plan completed!")
        return complete_plan

# Initialize orchestrator
print("Starting AI Travel Planner API...")
orchestrator = TravelPlannerOrchestrator()

# API Endpoints
@app.get("/")
def read_root():
    return {
        "message": "AI Travel Planner API",
        "version": "1.0",
        "ai_enabled": GEMINI_AVAILABLE and bool(GEMINI_API_KEY),
        "endpoints": {
            "POST /api/plan-trip": "Create a complete travel plan"
        }
    }

@app.post("/api/plan-trip")
async def plan_trip(request: TravelRequest):
    """
    Create a comprehensive travel plan using multi-agent system
    """
    print("resuqest here ", request)
    try:
        # Validate input
        print("resquet destination", request.destination)
        if not request.destination:
            raise HTTPException(status_code=400, detail="Destination is required")

        # Create travel plan using orchestrator
        travel_plan = orchestrator.create_travel_plan(request)
        os.makedirs("logs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logs/travel_plan_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(travel_plan, f, indent=4)

        print(f"Saved travel plan to: {filename}")

        return travel_plan

    except Exception as e:
        print(f"Error creating travel plan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating travel plan: {str(e)}")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "agents": 7,
        "ai_configured": GEMINI_AVAILABLE and bool(GEMINI_API_KEY)
    }

# Run with: uvicorn main:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
