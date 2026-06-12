import os
import io
import json
import base64
import requests
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai

from models import db, State, Crop, Soil, CropSoil, Disease, Chemical
from seed import seed_database

# Load environment variables
load_dotenv(override=True)

# Configure Gemini API (Legacy fallback)
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

# Configure Azure OpenAI API
azure_openai_key = os.getenv("AZURE_OPENAI_KEY")
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_openai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION")

def call_azure_openai(messages, temperature=0.7):
    if not azure_openai_key or not azure_openai_endpoint:
        raise Exception("Azure OpenAI is not configured in the backend .env file.")
        
    url = f"{azure_openai_endpoint.rstrip('/')}/openai/deployments/{azure_openai_deployment}/chat/completions?api-version={azure_openai_api_version}"
    headers = {
        "api-key": azure_openai_key,
        "Content-Type": "application/json"
    }
    payload = {
        "messages": messages,
        "temperature": temperature
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Azure OpenAI API returned error {response.status_code}: {response.text}")
    return response.json()["choices"][0]["message"]["content"]


app = Flask(__name__)
CORS(app)

# Database Configuration (MySQL or fallback to local SQLite)
database_url = os.getenv("DATABASE_URL")
if not database_url:
    # Use SQLite by default for hassle-free out-of-the-box local execution
    db_path = os.path.join(os.path.dirname(__file__), "agriculture.db")
    database_url = f"sqlite:///{db_path}"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# In-memory activity log for admin actions
activity_logs = [
    {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "action": "Database initialized", "status": "Success"},
    {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "action": "Standard seed dataset loaded", "status": "Success"}
]

def log_activity(action, status="Success"):
    activity_logs.insert(0, {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "status": status
    })
    # Keep only the latest 30 logs
    if len(activity_logs) > 30:
        activity_logs.pop()

# Setup database & seed automatically on startup if empty
with app.app_context():
    db_needs_reset = False
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if 'crops' in inspector.get_table_names():
            columns = [c['name'] for c in inspector.get_columns('crops')]
            if 'msp' not in columns:
                db_needs_reset = True
                print("Database schema out of date (missing 'msp' column). Resetting database...")
    except Exception as e:
        print("Error checking database schema:", e)

    if db_needs_reset:
        try:
            db.drop_all()
            db_path = os.path.join(os.path.dirname(__file__), "agriculture.db")
            if os.path.exists(db_path):
                # Close connection first if needed, but drop_all is usually enough.
                # Just in case, try to delete the file
                pass
        except Exception as e:
            print("Error dropping tables:", e)

    db.create_all()
    # If no states exist, assume DB is unseeded
    if State.query.first() is None:
        print("Database is empty. Seeding realistic agricultural dataset...")
        seed_database()

# Health check
@app.route("/")
def index():
    return jsonify({
        "status": "online",
        "message": "AgriFuture API is running.",
        "database": "MySQL" if database_url.startswith("mysql") else "SQLite",
        "timestamp": datetime.now().isoformat()
    })

# --- ADMIN STATS & LOGS ---
@app.route("/api/admin/stats", methods=["GET"])
def get_admin_stats():
    try:
        return jsonify({
            "total_states": State.query.count(),
            "total_crops": Crop.query.count(),
            "total_soils": Soil.query.count(),
            "total_diseases": Disease.query.count(),
            "total_chemicals": Chemical.query.count(),
            "activity_logs": activity_logs
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- STATE ENDPOINTS ---
@app.route("/api/states", methods=["GET"])
def get_states():
    states = State.query.all()
    return jsonify([s.to_dict() for s in states])

@app.route("/api/states/<int:id>", methods=["GET"])
def get_state(id):
    state = State.query.get_or_404(id)
    # Include major crops in state detail
    res = state.to_dict()
    res["crops"] = [c.to_dict() for c in state.crops]
    return jsonify(res)

@app.route("/api/states", methods=["POST"])
def create_state():
    data = request.json
    if not data or not data.get("state_name"):
        return jsonify({"error": "Missing 'state_name'"}), 400
    
    try:
        new_state = State(
            state_name=data["state_name"],
            climate=data.get("climate", "Tropical"),
            description=data.get("description", "")
        )
        db.session.add(new_state)
        db.session.commit()
        log_activity(f"Created State: {new_state.state_name}")
        return jsonify(new_state.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route("/api/states/<int:id>", methods=["PUT"])
def update_state(id):
    state = State.query.get_or_404(id)
    data = request.json or {}
    
    try:
        if "state_name" in data:
            state.state_name = data["state_name"]
        if "climate" in data:
            state.climate = data["climate"]
        if "description" in data:
            state.description = data["description"]
            
        db.session.commit()
        log_activity(f"Updated State: {state.state_name}")
        return jsonify(state.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route("/api/states/<int:id>", methods=["DELETE"])
def delete_state(id):
    state = State.query.get_or_404(id)
    name = state.state_name
    try:
        db.session.delete(state)
        db.session.commit()
        log_activity(f"Deleted State: {name}")
        return jsonify({"message": f"State {name} deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# --- CROP ENDPOINTS ---
@app.route("/api/crops", methods=["GET"])
def get_crops():
    crops = Crop.query.all()
    return jsonify([c.to_dict() for c in crops])

@app.route("/api/crops/<int:id>", methods=["GET"])
def get_crop(id):
    crop = Crop.query.get_or_404(id)
    res = crop.to_dict()
    res["diseases"] = [d.to_dict() for d in crop.diseases]
    return jsonify(res)

@app.route("/api/crops", methods=["POST"])
def create_crop():
    data = request.json
    if not data or not data.get("crop_name") or (not data.get("state_id") and not data.get("state_ids")):
        return jsonify({"error": "Missing 'crop_name' or state locations"}), 400
    
    try:
        new_crop = Crop(
            crop_name=data["crop_name"],
            scientific_name=data.get("scientific_name", "N/A"),
            season=data.get("season", "Kharif"),
            water_requirement=data.get("water_requirement", "Medium"),
            yield_val=data.get("yield", "N/A"),
            image_url=data.get("image_url") or f"/api/placeholder/400/300?crop={data['crop_name'].lower().replace(' ', '_')}",
            msp=data.get("msp", "N/A")
        )
        db.session.add(new_crop)
        
        # Link states
        state_ids = data.get("state_ids")
        if not state_ids and data.get("state_id"):
            state_ids = [int(data["state_id"])]
        if state_ids:
            for st_id in state_ids:
                state_obj = State.query.get(st_id)
                if state_obj:
                    new_crop.states.append(state_obj)
        
        # Link suitable soils if provided
        soil_ids = data.get("soil_ids") or []
        for s_id in soil_ids:
            soil_obj = Soil.query.get(s_id)
            if soil_obj:
                new_crop.soils.append(soil_obj)
                
        db.session.commit()
        log_activity(f"Created Crop: {new_crop.crop_name}")
        return jsonify(new_crop.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route("/api/crops/<int:id>", methods=["PUT"])
def update_crop(id):
    crop = Crop.query.get_or_404(id)
    data = request.json or {}
    
    try:
        if "crop_name" in data:
            crop.crop_name = data["crop_name"]
        if "scientific_name" in data:
            crop.scientific_name = data["scientific_name"]
        if "season" in data:
            crop.season = data["season"]
        if "water_requirement" in data:
            crop.water_requirement = data["water_requirement"]
        if "yield" in data:
            crop.yield_val = data["yield"]
        if "msp" in data:
            crop.msp = data["msp"]
        if "image_url" in data:
            crop.image_url = data["image_url"]
            
        # Update states if provided
        if "state_ids" in data or "state_id" in data:
            crop.states = []
            state_ids = data.get("state_ids")
            if not state_ids and data.get("state_id"):
                state_ids = [int(data["state_id"])]
            if state_ids:
                for st_id in state_ids:
                    state_obj = State.query.get(st_id)
                    if state_obj:
                        crop.states.append(state_obj)
            
        # Update soils if provided
        if "soil_ids" in data:
            # Clear old soils
            crop.soils = []
            for s_id in data["soil_ids"]:
                soil_obj = Soil.query.get(s_id)
                if soil_obj:
                    crop.soils.append(soil_obj)
        db.session.commit()
        log_activity(f"Updated Crop: {crop.crop_name}")
        return jsonify(crop.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route("/api/crops/<int:id>", methods=["DELETE"])
def delete_crop(id):
    crop = Crop.query.get_or_404(id)
    name = crop.crop_name
    try:
        db.session.delete(crop)
        db.session.commit()
        log_activity(f"Deleted Crop: {name}")
        return jsonify({"message": f"Crop {name} deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# --- SOIL ENDPOINTS ---
@app.route("/api/soils", methods=["GET"])
def get_soils():
    soils = Soil.query.all()
    return jsonify([s.to_dict() for s in soils])

@app.route("/api/soils/<int:id>", methods=["GET"])
def get_soil(id):
    soil = Soil.query.get_or_404(id)
    return jsonify(soil.to_dict())

@app.route("/api/soils", methods=["POST"])
def create_soil():
    data = request.json
    if not data or not data.get("soil_name"):
        return jsonify({"error": "Missing 'soil_name'"}), 400
    
    try:
        new_soil = Soil(
            soil_name=data["soil_name"],
            characteristics=data.get("characteristics", ""),
            ph_range=data.get("ph_range", "6.5 - 7.5")
        )
        db.session.add(new_soil)
        db.session.commit()
        log_activity(f"Created Soil Type: {new_soil.soil_name}")
        return jsonify(new_soil.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route("/api/soils/<int:id>", methods=["PUT"])
def update_soil(id):
    soil = Soil.query.get_or_404(id)
    data = request.json or {}
    
    try:
        if "soil_name" in data:
            soil.soil_name = data["soil_name"]
        if "characteristics" in data:
            soil.characteristics = data["characteristics"]
        if "ph_range" in data:
            soil.ph_range = data["ph_range"]
            
        db.session.commit()
        log_activity(f"Updated Soil Type: {soil.soil_name}")
        return jsonify(soil.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route("/api/soils/<int:id>", methods=["DELETE"])
def delete_soil(id):
    soil = Soil.query.get_or_404(id)
    name = soil.soil_name
    try:
        db.session.delete(soil)
        db.session.commit()
        log_activity(f"Deleted Soil Type: {name}")
        return jsonify({"message": f"Soil type {name} deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# --- DISEASE ENDPOINTS ---
@app.route("/api/diseases", methods=["GET"])
def get_diseases():
    diseases = Disease.query.all()
    return jsonify([d.to_dict() for d in diseases])

@app.route("/api/diseases/<int:id>", methods=["GET"])
def get_disease(id):
    disease = Disease.query.get_or_404(id)
    res = disease.to_dict()
    res["chemicals"] = [c.to_dict() for c in disease.chemicals]
    return jsonify(res)

@app.route("/api/diseases", methods=["POST"])
def create_disease():
    data = request.json
    if not data or not data.get("disease_name") or not data.get("crop_id"):
        return jsonify({"error": "Missing 'disease_name' or 'crop_id'"}), 400
    
    try:
        new_disease = Disease(
            disease_name=data["disease_name"],
            symptoms=data.get("symptoms", ""),
            causes=data.get("causes", ""),
            prevention=data.get("prevention", ""),
            crop_id=int(data["crop_id"]),
            image_url=data.get("image_url") or f"/api/placeholder/400/300?disease={data['disease_name'].lower().replace(' ', '_')}"
        )
        db.session.add(new_disease)
        db.session.commit()
        log_activity(f"Created Disease: {new_disease.disease_name}")
        return jsonify(new_disease.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route("/api/diseases/<int:id>", methods=["PUT"])
def update_disease(id):
    disease = Disease.query.get_or_404(id)
    data = request.json or {}
    
    try:
        if "disease_name" in data:
            disease.disease_name = data["disease_name"]
        if "symptoms" in data:
            disease.symptoms = data["symptoms"]
        if "causes" in data:
            disease.causes = data["causes"]
        if "prevention" in data:
            disease.prevention = data["prevention"]
        if "crop_id" in data:
            disease.crop_id = int(data["crop_id"])
        if "image_url" in data:
            disease.image_url = data["image_url"]
            
        db.session.commit()
        log_activity(f"Updated Disease: {disease.disease_name}")
        return jsonify(disease.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route("/api/diseases/<int:id>", methods=["DELETE"])
def delete_disease(id):
    disease = Disease.query.get_or_404(id)
    name = disease.disease_name
    try:
        db.session.delete(disease)
        db.session.commit()
        log_activity(f"Deleted Disease: {name}")
        return jsonify({"message": f"Disease {name} deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# --- CHEMICAL ENDPOINTS ---
@app.route("/api/chemicals", methods=["GET"])
def get_chemicals():
    chemicals = Chemical.query.all()
    return jsonify([c.to_dict() for c in chemicals])

@app.route("/api/chemicals/<int:id>", methods=["GET"])
def get_chemical(id):
    chemical = Chemical.query.get_or_404(id)
    return jsonify(chemical.to_dict())

@app.route("/api/chemicals", methods=["POST"])
def create_chemical():
    data = request.json
    if not data or not data.get("chemical_name") or not data.get("disease_id"):
        return jsonify({"error": "Missing 'chemical_name' or 'disease_id'"}), 400
    
    try:
        new_chem = Chemical(
            chemical_name=data["chemical_name"],
            chemical_type=data.get("chemical_type", "Fungicide"),
            dosage=data.get("dosage", ""),
            application_method=data.get("application_method", ""),
            safety_precautions=data.get("safety_precautions", ""),
            disease_id=int(data["disease_id"])
        )
        db.session.add(new_chem)
        db.session.commit()
        log_activity(f"Created Chemical Rec: {new_chem.chemical_name}")
        return jsonify(new_chem.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route("/api/chemicals/<int:id>", methods=["PUT"])
def update_chemical(id):
    chemical = Chemical.query.get_or_404(id)
    data = request.json or {}
    
    try:
        if "chemical_name" in data:
            chemical.chemical_name = data["chemical_name"]
        if "chemical_type" in data:
            chemical.chemical_type = data["chemical_type"]
        if "dosage" in data:
            chemical.dosage = data["dosage"]
        if "application_method" in data:
            chemical.application_method = data["application_method"]
        if "safety_precautions" in data:
            chemical.safety_precautions = data["safety_precautions"]
        if "disease_id" in data:
            chemical.disease_id = int(data["disease_id"])
            
        db.session.commit()
        log_activity(f"Updated Chemical Rec: {chemical.chemical_name}")
        return jsonify(chemical.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route("/api/chemicals/<int:id>", methods=["DELETE"])
def delete_chemical(id):
    chemical = Chemical.query.get_or_404(id)
    name = chemical.chemical_name
    try:
        db.session.delete(chemical)
        db.session.commit()
        log_activity(f"Deleted Chemical Rec: {name}")
        return jsonify({"message": f"Chemical recommendation {name} deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# --- GEMINI API INTEGRATIONS ---

@app.route("/api/gemini/diagnose", methods=["POST"])
def gemini_diagnose():
    if not azure_openai_key:
        return jsonify({
            "error": "Azure OpenAI key is not configured in the backend .env file.",
            "code": "API_KEY_MISSING"
        }), 400

    if "image" not in request.files:
        return jsonify({"error": "No image file provided in request."}), 400

    image_file = request.files["image"]
    crop_name = request.form.get("crop_name", "unknown plant")

    try:
        # Load image bytes
        img_bytes = image_file.read()
        image = Image.open(io.BytesIO(img_bytes))
        img_format = image.format or "JPEG"
        img_mime = f"image/{img_format.lower()}"
        
        # Base64 encode the image
        base64_image = base64.b64encode(img_bytes).decode('utf-8')

        prompt = f"""
        You are an expert plant pathologist. 
        Analyze the health of this plant leaf image. The user suspects it is a '{crop_name}' plant.
        Identify the disease or condition.
        Return your analysis STRICTLY in JSON format with the following keys, without markdown formatting around the JSON (do NOT include ```json or ``` tags):
        {{
            "crop_name": "Detected crop name (e.g. Tomato)",
            "disease_name": "Diagnosed disease name or 'Healthy'",
            "confidence": "Estimated confidence (e.g. 94.2%)",
            "symptoms": "A brief 2-sentence description of the visual symptoms",
            "causes": "What causes this issue",
            "prevention": "Practical prevention guidelines",
            "recommended_chemical": "Specific active chemical treatment (fungicide/pesticide) or 'None' if healthy",
            "dosage": "Suggested dosage (e.g., 2 ml/litre)",
            "application_method": "How to apply (e.g., Foliar Spray)",
            "safety_precautions": "Safety measures during application"
        }}
        """

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{img_mime};base64,{base64_image}"
                        }
                    }
                ]
            }
        ]

        response_text = call_azure_openai(messages, temperature=0.2).strip()
        
        # Strip code fences if the model included them anyway
        if response_text.startswith("```"):
            response_text = "\n".join(response_text.split("\n")[1:])
        if response_text.endswith("```"):
            response_text = "\n".join(response_text.split("\n")[:-1])
            
        response_text = response_text.strip()
        
        result_json = json.loads(response_text)
        log_activity(f"AI diagnosed crop leaf: {result_json.get('disease_name', 'Unknown')}")
        return jsonify(result_json)
        
    except Exception as e:
        return jsonify({"error": f"Failed to run AI diagnostics: {str(e)}"}), 500


@app.route("/api/gemini/chat", methods=["POST"])
def gemini_chat():
    if not azure_openai_key:
        return jsonify({
            "error": "Azure OpenAI key is not configured in the backend .env file.",
            "code": "API_KEY_MISSING"
        }), 400

    data = request.json or {}
    message = data.get("message")
    history = data.get("history") or [] # List of {"role": "user"|"model", "parts": [str]}
    language_code = data.get("language", "en-IN")

    if not message:
        return jsonify({"error": "Missing 'message' parameter."}), 400

    try:
        lang_instruction = "Respond strictly in English. Write in clear, standard English."
        if language_code == "hi-IN":
            lang_instruction = """
            Respond strictly in Hindi. Your output MUST be entirely in the Hindi language, using the Devanagari script.
            Do not use robotic, direct English-to-Hindi translations. Use warm, natural, humanized, conversational Hindi as spoken by farmers in North India (e.g., use greetings like 'राम राम भाई जी' or 'नमस्ते किसान भाइयों', and use everyday agricultural words like 'धान' or 'चावल की फसल', 'खाद', 'सिंचाई'). Keep it simple, friendly, and easy to understand.
            """
        elif language_code == "te-IN":
            lang_instruction = """
            Respond strictly in Telugu. Your output MUST be entirely in the Telugu language, using the Telugu script.
            Do not use robotic, direct English-to-Telugu translations (e.g., NEVER use 'బియ్యం పంట' because 'బియ్యం' means uncooked rice grains; always use 'వరి' or 'వరి పంట' for the crop in the field).
            Use natural, warm, humanized, conversational Telugu as spoken by real farmers in Andhra Pradesh and Telangana. Add polite suffixes like 'అండీ' (andi) to keep the tone friendly (e.g., 'నమస్తే అండీ', 'సలహాలు ఇక్కడ ఉన్నాయి చూడండి', 'చేయండి అండీ'). Explain advice in a simple, easy, neighborly manner. Do not write Telugu words in English characters.
            """
            
        system_instruction = f"""
        You are 'CropCare AI', a friendly, knowledgeable agricultural chatbot assistant for farmers in India.
        Provide practical, clear farming advice about crops, soil, climate, fertilizers, and disease management.
        
        Language Instruction:
        {lang_instruction}
        
        Keep your advice actionable and focused on low-cost and organic alternatives where possible.
        """
        
        messages = [{"role": "system", "content": system_instruction}]
        
        for h in history[-10:]: # Keep last 10 messages for context
            role = "user" if h.get("role") == "user" else "assistant"
            parts = h.get("parts")
            content = parts[0] if isinstance(parts, list) and len(parts) > 0 else ""
            messages.append({"role": role, "content": content})
            
        messages.append({"role": "user", "content": message})
        
        reply = call_azure_openai(messages, temperature=0.7)
        return jsonify({"reply": reply.strip()})
        
    except Exception as e:
        return jsonify({"error": f"Failed to get reply: {str(e)}"}), 500


@app.route("/api/gemini/schedule", methods=["POST"])
def gemini_schedule():
    if not azure_openai_key:
        return jsonify({
            "error": "Azure OpenAI key is not configured in the backend .env file.",
            "code": "API_KEY_MISSING"
        }), 400

    data = request.json or {}
    soil_type = data.get("soil_type")
    crop_type = data.get("crop_type")
    acres = data.get("acres")
    irrigation_type = data.get("irrigation_type")
    state_name = data.get("state_name")
    previous_crop = data.get("previous_crop")
    previous_yield = data.get("previous_yield")

    if not crop_type or not soil_type:
        return jsonify({"error": "Missing 'crop_type' or 'soil_type' parameters."}), 400

    try:
        prompt = f"""
        You are an expert agronomist advisor in India. A farmer wants a customized crop cultivation schedule and suggestions based on their farm details.
        
        Farmer Profile:
        - Crop to grow: {crop_type}
        - Soil type: {soil_type}
        - Farm size: {acres} acres
        - Irrigation method: {irrigation_type}
        - Location (State/Region): {state_name}
        - Previous crop grown: {previous_crop}
        - Previous yield obtained: {previous_yield}
        
        Generate a highly structured, comprehensive, and practical cultivation schedule and suggestions.
        Provide the response STRICTLY as a raw JSON object (with no ```json code fences or markdown formatting) containing the following structure:
        {{
            "crop_schedule": [
                {{
                    "phase": "Land Preparation & Pre-sowing",
                    "timeline": "Day -10 to Day 0",
                    "activities": [
                        "Deep plow the field 2-3 times to expose soil pathogens to sun.",
                        "Incorporate 5-10 tons of well-decomposed Farmyard Manure (FYM) per acre."
                    ],
                    "irrigation_advice": "Apply pre-sowing irrigation if soil moisture is low.",
                    "fertilizer_dosage": "Apply baseline Phosphorus (SSP) at 50 kg per acre."
                }},
                {{
                    "phase": "Sowing / Transplanting",
                    "timeline": "Day 1 to Day 5",
                    "activities": [
                        "Treat seeds with Trichoderma viride at 5g/kg to prevent root rot.",
                        "Sow seeds at a depth of 2-3 cm with spacing of 30x10 cm."
                    ],
                    "irrigation_advice": "Maintain light moisture; do not waterlog the soil.",
                    "fertilizer_dosage": "Apply 20 kg Urea per acre as basal dose."
                }},
                {{
                    "phase": "Vegetative Growth & Weeding",
                    "timeline": "Day 15 to Day 45",
                    "activities": [
                        "Perform hand weeding or apply selective pre-emergence herbicide.",
                        "Monitor closely for early signs of leaf spot or insect pests."
                    ],
                    "irrigation_advice": "Irrigate at critical crop stages (tillering/branching).",
                    "fertilizer_dosage": "Top dress with 30 kg Urea per acre after first weeding."
                }},
                {{
                    "phase": "Flowering & Harvesting",
                    "timeline": "Day 50 to Day 90",
                    "activities": [
                        "Harvest when 80-90% of the grains/pods turn golden brown.",
                        "Dry the harvested crop in clean yards to reach safe moisture levels."
                    ],
                    "irrigation_advice": "Stop irrigation 10-15 days before harvest.",
                    "fertilizer_dosage": "No chemical fertilizers at this stage. Foliar spray of Potassium if needed."
                }}
            ],
            "general_suggestions": [
                "Since you grew {previous_crop} previously, ensure crop rotation is maintained to prevent pest build-up.",
                "Leverage organic mulching to conserve moisture, which is highly suited for your {irrigation_type} system."
            ],
            "soil_and_fertilizer_tips": [
                "Your {soil_type} has specific drainage qualities. Work on improving soil organic carbon.",
                "Perform a soil health test annually to calibrate NPK application accurately."
            ],
            "warnings": [
                "High risk of waterlogging on {soil_type} if flood irrigation is overdone.",
                "Watch out for crop-specific pests that transfer from {previous_crop}."
            ]
        }}
        
        Ensure that all dates, dosages, and warnings are highly realistic for Indian agriculture and tailored to {acres} acres of land.
        """

        messages = [{"role": "user", "content": prompt}]
        response_text = call_azure_openai(messages, temperature=0.3).strip()
        
        # Strip code fences if the model included them anyway
        if response_text.startswith("```"):
            response_text = "\n".join(response_text.split("\n")[1:])
        if response_text.endswith("```"):
            response_text = "\n".join(response_text.split("\n")[:-1])
            
        response_text = response_text.strip()
        
        result_json = json.loads(response_text)
        log_activity(f"AI generated cultivation schedule for {crop_type} on {soil_type}")
        return jsonify(result_json)
        
    except Exception as e:
        return jsonify({"error": f"Failed to generate cultivation schedule: {str(e)}"}), 500


def parse_msp_numeric(msp_str):
    if not msp_str or msp_str == "N/A":
        return None
    # Extract digits and clean formatting
    digits = [c for c in msp_str if c.isdigit()]
    if not digits:
        return None
    try:
        return float("".join(digits))
    except ValueError:
        return None

def get_historical_msp(crop_name, base_val):
    # Use deterministic seed based on crop name
    seed = sum(ord(c) for c in crop_name)
    historical = []
    # Work backwards from 2025 (current seeded data) to 2013
    for yr in range(2013, 2026):
        years_diff = yr - 2025
        # Average annual growth of ~5.2%
        val = base_val * (1.052 ** years_diff)
        # Deterministic wobble of +/- 2.5%
        wobble_percent = (((seed * yr) % 50) - 25) / 1000.0
        val_wobbled = val * (1 + wobble_percent)
        # Round to nearest 5
        val_rounded = round(val_wobbled / 5.0) * 5
        historical.append((yr, val_rounded))
    return historical

def predict_crop_msp(crop_name, base_val):
    historical = get_historical_msp(crop_name, base_val)
    n = len(historical)
    sum_x = sum(x for x, y in historical)
    sum_y = sum(y for x, y in historical)
    sum_xy = sum(x * y for x, y in historical)
    sum_x2 = sum(x * x for x, y in historical)
    
    denominator = (n * sum_x2 - sum_x * sum_x)
    if denominator == 0:
        slope = 0.0
        intercept = base_val
    else:
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n
        
    predictions = []
    for yr in range(2026, 2037):
        pred_val = slope * yr + intercept
        # MSP in India never decreases year-over-year
        pred_val = max(pred_val, base_val)
        pred_val_rounded = round(pred_val / 5.0) * 5
        predictions.append((yr, pred_val_rounded))
        
    return historical, predictions

@app.route("/api/predict-msp", methods=["GET"])
def predict_msp():
    year_param = request.args.get("year", "2026")
    try:
        selected_year = int(year_param)
    except ValueError:
        return jsonify({"error": "Invalid year parameter. Must be an integer."}), 400
        
    if selected_year < 2026 or selected_year > 2036:
        return jsonify({"error": "Year must be between 2026 and 2036."}), 400
        
    try:
        crops_list = Crop.query.all()
        predictions_data = []
        best_crop = None
        max_growth_rate = -999.0
        
        for crop in crops_list:
            base_val = parse_msp_numeric(crop.msp)
            if base_val is None or base_val <= 0:
                continue
                
            historical, future = predict_crop_msp(crop.crop_name, base_val)
            
            # Find the predicted value for the selected year
            pred_val_for_year = None
            for yr, val in future:
                if yr == selected_year:
                    pred_val_for_year = val
                    break
                    
            if pred_val_for_year is None:
                continue
                
            growth_rate = ((pred_val_for_year - base_val) / base_val) * 100.0
            
            # Record best crop
            if growth_rate > max_growth_rate:
                max_growth_rate = growth_rate
                best_crop = {
                    "crop_id": crop.id,
                    "crop_name": crop.crop_name,
                    "base_msp": base_val,
                    "predicted_msp": pred_val_for_year,
                    "growth_rate_pct": round(growth_rate, 2),
                    "season": crop.season,
                    "image_url": crop.image_url
                }
                
            predictions_data.append({
                "crop_id": crop.id,
                "crop_name": crop.crop_name,
                "base_msp": base_val,
                "predicted_msp": pred_val_for_year,
                "growth_rate_pct": round(growth_rate, 2),
                "season": crop.season,
                "historical": [{"year": yr, "value": val} for yr, val in historical],
                "future": [{"year": yr, "value": val} for yr, val in future]
            })
            
        return jsonify({
            "selected_year": selected_year,
            "best_crop": best_crop,
            "predictions": predictions_data
        })
    except Exception as e:
        return jsonify({"error": f"Failed to predict MSP: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)

