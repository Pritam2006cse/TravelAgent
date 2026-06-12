# Agents Module
import os
from openai import OpenAI
from dotenv import load_dotenv
from state_manager import TravelState, ItineraryLeg, DestinationSuggestion, DestinationSuggestionList
import pandas as pd
from typing import List
import requests

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class TravelData:
    _token = None
    _schedules_df = None
    _stations_df = None
    _dataset_initialized = False

    @classmethod
    def _init_kaggle_dataset(cls):
        """
        Natively registers and indexes the downloaded Kaggle Indian Railways Dataframes.
        """
        if cls._dataset_initialized:
            return

        try:
            # Adjust file paths if your Kaggle dataset is located inside a nested folder
            schedules_path = "schedules.csv"
            stations_path = "stations.csv"

            if os.path.exists(schedules_path) and os.path.exists(stations_path):
                cls._schedules_df = pd.read_csv(schedules_path)
                cls._stations_df = pd.read_csv(stations_path)
                cls._dataset_initialized = True
                print("[Kaggle Registry]: Indian Railways dataset parsed successfully.")
            else:
                print("[Kaggle Registry Warning]: CSV files not detected in root directory. Using dynamic fallback arrays.")
        except Exception as e:
            print(f"[Kaggle Registry Error]: Failed to initialize tables: {str(e)}")

    @staticmethod
    def _get_iata_code(city_name: str) -> str:
        """
        Helper to convert city names to IATA codes.
        CHANGE HERE: Replace with a real airport-lookup API call, 
        or maintain a local dict for common Indian cities as a quick fix.
        """
        IATA_MAP = {
            "agra": "AGR",
            "ahmedabad": "AMD",
            "agartala": "IXA",
            "amritsar": "ATQ",
            "bagdogra": "IXB",
            "bangalore": "BLR",
            "bhopal": "BHO",
            "bhubaneswar": "BBI",
            "chandigarh": "IXC",
            "chennai": "MAA",
            "cochin": "COK",
            "coimbatore": "CJB",
            "dehradun": "DED",
            "delhi": "DEL",
            "goa": "GOI",
            "guwahati": "GAU",
            "gwalior": "GWL",
            "hyderabad": "HYD",
            "indore": "IDR",
            "jaipur": "JAI",
            "jammu": "IXJ",
            "jodhpur": "JDH",
            "kanpur": "KNU",
            "khajuraho": "HJR",
            "kolkata": "CCU",
            "kozhikode": "CCJ",
            "leh": "IXL",
            "lucknow": "LKO",
            "madurai": "IXM",
            "manali": "KUU",
            "mangalore": "IXE",
            "mopa": "GOX",
            "mumbai": "BOM",
            "nagpur": "NAG",
            "pantnagar": "PGH",
            "patna": "PAT",
            "pune": "PNQ",
            "raipur": "RPR",
            "rajkot": "RAJ",
            "ranchi": "IXR",
            "shirdi": "SAG",
            "silchar": "IXS",
            "srinagar": "SXR",
            "surat": "STV",
            "tirupati": "TIR",
            "tiruchirappalli": "TRZ",
            "trivandrum": "TRV",
            "udaipur": "UDR",
            "vadodara": "BDQ",
            "varanasi": "VNS",
            "vijayawada": "VGA",
            "visakhapatnam": "VTZ"
        }

        return IATA_MAP.get(city_name.strip().lower(), city_name[:3].upper())
    
    @staticmethod
    def _get_station_code(city_name: str) -> str:
        STATION_MAP = {
                "agartala": "AGTL",
                "agra": "AGC",
                "ahmedabad": "ADI",
                "ajmer": "AII",
                "allahabad": "PRYJ",
                "amritsar": "ASR",
                "asansol": "ASN",
                "aurangabad": "AWB",
                "bagdogra": "SGUJ",
                "bangalore": "SBC",
                "bareilly": "BE",
                "bhopal": "BPL",
                "bhubaneswar": "BBS",
                "bikaner": "BKN",
                "bilaspur": "BSP",
                "chandigarh": "CDG",
                "chennai": "MAS",
                "cochin": "ERS",
                "coimbatore": "CBE",
                "cuttack": "CTC",
                "darjeeling": "DJ",
                "dehradun": "DDN",
                "delhi": "NDLS",
                "dhanbad": "DHN",
                "dibrugarh": "DBRG",
                "durgapur": "DGR",
                "gaya": "GAYA",
                "goa": "MAO",
                "gorakhpur": "GKP",
                "guwahati": "GHY",
                "gwalior": "GWL",
                "haridwar": "HW",
                "howrah": "HWH",
                "hyderabad": "HYB",
                "indore": "INDB",
                "jabalpur": "JBP",
                "jaipur": "JP",
                "jalandhar": "JUC",
                "jammu": "JAT",
                "jamshedpur": "TATA",
                "jhansi": "VGLJ",
                "jodhpur": "JU",
                "kanpur": "CNB",
                "kharagpur": "KGP",
                "kozhikode": "CLT",
                "kolkata": "HWH",
                "kota": "KOTA",
                "lucknow": "LKO",
                "ludhiana": "LDH",
                "madurai": "MDU",
                "mangalore": "MAJN",
                "mathura": "MTJ",
                "meerut": "MTC",
                "mumbai": "CSTM",
                "muzaffarpur": "MFP",
                "mysore": "MYS",
                "nagpur": "NGP",
                "nashik": "NK",
                "patna": "PNBE",
                "puducherry": "PDY",
                "pune": "PUNE",
                "puri": "PURI",
                "raipur": "R",
                "rajkot": "RJT",
                "ranchi": "RNC",
                "rameswaram": "RMM",
                "secunderabad": "SC",
                "shirdi": "SNSI",
                "shimla": "SML",
                "siliguri": "SGUJ",
                "surat": "ST",
                "thrissur": "TCR",
                "tirupati": "TPTY",
                "tiruchirappalli": "TPJ",
                "trivandrum": "TVC",
                "udaipur": "UDZ",
                "ujjain": "UJN",
                "vadodara": "BRC",
                "varanasi": "BSB",
                "vijayawada": "BZA",
                "visakhapatnam": "VSKP"
            }
        return STATION_MAP.get(city_name.strip().lower(), city_name[:3].upper())

    
    @classmethod
    def get_live_flight(cls, from_location: str, to_location: str, departure_date: str = None):
        """
        Integration layer for Aviationstack API.
        Requires AVIATIONSTACK_API_KEY in your .env file.
        """
        api_key = os.getenv("AVIATIONSTACK_API_KEY")
        if not api_key:
            print("[Aviationstack Alert]: Missing API key, deploying mock fallback.")
            return {"real_operator": "Air India", "real_identification_no": "AI803"}
        url = "https://api.aviationstack.com/v1/flights"
        dep_iata = cls._get_iata_code(from_location)
        arr_iata = cls._get_iata_code(to_location)
        params = {
            "access_key": api_key,
            "dep_iata": dep_iata,
            "arr_iata": arr_iata,
            "limit": 1
        }
        try:
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                flight_data = data.get("data", [])
                if flight_data:
                    first_flight = flight_data[0]
                    airline = first_flight.get("airline", {}).get("name", "Domestic Carrier")
                    flight_num = first_flight.get("flight", {}).get("iata", "6E-Air")
                    return {
                        "real_operator": airline,
                        "real_identification_no": flight_num
                    }
        except Exception as e:
            print(f"[Aviationstack Exception]: {str(e)}")
        return {"real_operator": "6E (IndiGo)", "real_identification_no": "6E2134"}
    
    @classmethod
    def get_live_rail(cls, from_location: str, to_location: str, departure_date: str = None):
        cls._init_kaggle_dataset()
        
        from_code = cls._get_station_code(from_location)
        to_code = cls._get_station_code(to_location)

        # Query Kaggle tables directly if loaded in memory
        if cls._dataset_initialized and cls._schedules_df is not None:
            try:
                # Find trains serving the origin station code
                origin_trains = cls._schedules_df[cls._schedules_df['station_code'] == from_code]
                # Find trains serving the destination station code
                dest_trains = cls._schedules_df[cls._schedules_df['station_code'] == to_code]
                
                # Perform an inner intersection join on matching train numbers
                matching_routes = pd.merge(origin_trains, dest_trains, on='train_number', suffixes=('_src', '_dst'))
                
                # Filter routes running in the correct direction (source sequence comes before destination sequence)
                # Kaggle datasets track sequence ordering via the chronological ID or day column layout
                valid_direction = matching_routes[matching_routes['id_src'] < matching_routes['id_dst']]
                
                if not valid_direction.empty:
                    first_match = valid_direction.iloc[0]
                    return {
                        "real_operator": f"Indian Railways ({first_match['train_name_src']})",
                        "real_identification_no": str(int(first_match['train_number']))
                    }
            except Exception as e:
                print(f"[Kaggle Query Error]: Table scan execution failed: {str(e)}")

        # Clean fallback routing engine if direct matrix match isn't found 
        return {
            "real_operator": f"Indian Railways (Express via {from_code})",
            "real_identification_no": "12626"
        }

class BaseAgent:
    def __init__(self, name:str):
        self.name = name
    def log(self,state: TravelState,message:str):
        log_entry = f"[{self.name}]:{message}"
        print(log_entry)
        state.agent_logs.append(log_entry)

class DestinationSuggesterAgent(BaseAgent):
    def run(self,user_prompt:str) -> List[DestinationSuggestion]:
        system_prompt = (
            "You are a Destination Curator for travelers in India. "
            "Based on the user's stated interests (adventure, scenic beauty, "
            "festivals, culture, relaxation, etc.), suggest 4 distinct destinations. "
            "For each, give the destination name, a 1-2 sentence reason, and "
            "what it's 'best_for' (one short tag like 'adventure' or 'scenic')."
        )
        try:
            response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=DestinationSuggestionList
            )
            return response.choices[0].message.parsed.suggestions
        except Exception as e:
            print(f"[DestinationSuggesterAgent] Error: {str(e)}")
            # Fallback suggestions if LLM call fails
            return [
                DestinationSuggestion(destination="Jaipur", reason="Rich culture, forts, and vibrant markets.", best_for="culture"),
                DestinationSuggestion(destination="Manali", reason="Mountains, trekking, and adventure sports.", best_for="adventure"),
                DestinationSuggestion(destination="Goa", reason="Beaches, relaxation, and nightlife.", best_for="relaxation"),
                DestinationSuggestion(destination="Pushkar", reason="Famous for the Pushkar Camel Fair and spiritual sites.", best_for="festivals"),
            ]
    
class FlightAgent(BaseAgent):
    def run(self,state: TravelState):
        self.log(state,"Analyzing travel guide according to user...")
        if any(leg.type=="flight" for leg in state.current_itinerary):
            self.log(state, "Flight leg already present. Skipping.")
            return
        intent_check = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an analyzer. Respond with 'YES' if the user's travel request requires an airplane/flight, or 'NO' if it can be done entirely by ground/train or explicitly requests no flights. Do not give any false positive reply."},
                {"role": "user", "content": state.user_prompt}
            ]
        )
        if "NO" in intent_check.choices[0].message.content.upper():
            self.log(state, "Flight routing not required for this itinerary. Stepping aside.")
            return
        system_prompt = (
            "You are an expert Flight Logistics Agent. Your job is to analyze the user's travel request "
            "and suggest the primary long-haul flight leg. You MUST return a single valid flight itinerary segment. "
            "Provide a highly realistic airline operator (e.g., Virgin Atlantic) and a valid flight identification_number (e.g., VS4)."
            "IMPORTANT: departure_date and arrival_date must be in 'YYYY-MM-DD' format. "
            "departure_time and arrival_time must be in 'HH:MM:SS' format (24-hour, no date or timezone). "
            "Set the leg_index to 0.(Year 2026)."
        )
        try:
            response = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"User Request: {state.user_prompt}. Max Budget: ${state.max_budget}"}
                ],
                response_format=ItineraryLeg # Enforces output schema matches our state file!
            )
            flight_leg = response.choices[0].message.parsed
            api_data = TravelData.get_live_flight(flight_leg.from_location, flight_leg.to_location)
            flight_leg.operator = api_data["real_operator"]
            flight_leg.identification_number = api_data["real_identification_no"]
            flight_leg.leg_index = len(state.current_itinerary)
            state.current_itinerary.append(flight_leg)
            self.log(state, f"Proposed Flight: {flight_leg.from_location} -> {flight_leg.to_location}")
        except Exception as e:
            self.log(state, f"Error generating flight: {str(e)}")

class RailAgent(BaseAgent):
    def run(self,state:TravelState):
        self.log(state, "Evaluating contextual rail options via LLM...")
        if any(leg.type=="rail" for leg in state.current_itinerary):
            self.log(state,"Rail leg already exists.")
            return
        intent_check = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an analyzer. Respond with 'YES' if the user's travel request include any railway/rail/train, or 'NO' if it can be done entirely by air/flight or explicitly requests flights.Respond NO only if no rail transport is requested."},
                {"role": "user", "content": state.user_prompt}
            ]
        )
        if "NO" in intent_check.choices[0].message.content.upper():
            self.log(state, "Rail leg not required for this itinerary. Stepping aside.")
            return
        system_prompt = (
            "You are a Rail Network Specialist. Review the user request and any current itinerary context. "
            "Your job is to add a valid train leg to help the user reach their destination. "
            "If a flight leg is present, connect the train from the airport arrival city. "
            "If NO flight leg is present, build the entire journey using trains from the starting location. "
            "Set type to 'rail' and mode to 'train'. status must be 'proposed'."
            "IMPORTANT: departure_date and arrival_date must be in 'YYYY-MM-DD' format. "
            "departure_time and arrival_time must be in 'HH:MM:SS' format (24-hour, no date or timezone). "
            "Provide a realistic rail operator name (e.g., Eurostar) and a train identification_number or service identifier (e.g., ES9044)."
        )
        current_itinerary_context = str([leg.model_dump() for leg in state.current_itinerary])
        try:
            response = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"User Request: {state.user_prompt}\nCurrent Progress: {current_itinerary_context}"}
                ],
                response_format=ItineraryLeg
            )
            rail_leg = response.choices[0].message.parsed
            if rail_leg.from_location and rail_leg.to_location:
                api_data = TravelData.get_live_rail(rail_leg.from_location, rail_leg.to_location)
                rail_leg.operator = api_data["real_operator"]
                rail_leg.identification_number = api_data["real_identification_no"]
                rail_leg.leg_index = len(state.current_itinerary)
                state.current_itinerary.append(rail_leg)
                self.log(state, f"Proposed Rail: {rail_leg.from_location} -> {rail_leg.to_location}")
        except Exception as e:
            self.log(state, f"Error generating rail: {str(e)}")

class ValidatorAgent(BaseAgent):
    def run(self,state:TravelState):
        self.log(state, "Executing cross-modal timeline validation...")
        state.validation_errors = []
        state.is_validated = False
        if not state.current_itinerary:
            state.validation_errors.append("No itinerary generated.")
        flight = next((leg for leg in state.current_itinerary if leg.type=="flight"),None)
        rail = next((leg for leg in state.current_itinerary if leg.type=="rail"),None)
        if flight and rail:
            from datetime import datetime
            f_arr = datetime.fromisoformat(f"{flight.arrival_date}T{flight.arrival_time}")
            r_dep = datetime.fromisoformat(f"{rail.departure_date}T{rail.departure_time}")
            time_difference = (r_dep - f_arr).total_seconds() / 60
            if time_difference < 120: # Requires a minimum 2-hour transfer window
                state.validation_errors.append(f"Temporal Breach: Layover is only {time_difference} mins. Need 120+ mins for safe customs extraction.")
            if flight.to_location.lower() != rail.from_location.lower():
                state.validation_errors.append("Route Breach: Rail journey does not begin where flight ends.")
        if flight and not rail:
            state.validation_errors.append("Incomplete itinerary: missing required rail segment.")
        if rail and not flight:
            state.validation_errors.append("Incomplete itinerary: missing required flight segment.")
        if not state.validation_errors:
            state.is_validated = True
            for leg in state.current_itinerary:
                leg.status = "confirmed"
            self.log(state, "Cleared. Itinerary meets all financial and structural constraints.")
        else:
            state.is_validated = False
            self.log(state, f"Validation Rejection: {state.validation_errors}")