import os
import io
import json
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

# Configure Gemini API
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)


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
            image_url=data.get("image_url") or f"/api/placeholder/400/300?crop={data['crop_name'].lower().replace(' ', '_')}"
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
    if not gemini_api_key:
        return jsonify({
            "error": "Gemini API key is not configured in the backend .env file.",
            "code": "API_KEY_MISSING"
        }), 400

    if "image" not in request.files:
        return jsonify({"error": "No image file provided in request."}), 400

    image_file = request.files["image"]
    crop_name = request.form.get("crop_name", "unknown plant")

    try:
        # Load image
        img_bytes = image_file.read()
        image = Image.open(io.BytesIO(img_bytes))

        # Initialize model
        model = genai.GenerativeModel('gemini-2.5-flash')

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

        response = model.generate_content([prompt, image])
        response_text = response.text.strip()
        
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
    if not gemini_api_key:
        return jsonify({
            "error": "Gemini API key is not configured in the backend .env file.",
            "code": "API_KEY_MISSING"
        }), 400

    data = request.json or {}
    message = data.get("message")
    history = data.get("history") or [] # List of {"role": "user"|"model", "parts": [str]}

    if not message:
        return jsonify({"error": "Missing 'message' parameter."}), 400

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Reconstruct chat session with system instruction
        system_instruction = """
        You are 'CropCare AI', a friendly, knowledgeable agricultural chatbot assistant for farmers in India.
        Provide practical, clear farming advice about crops, soil, climate, fertilizers, and disease management.
        Always match the language of the user's input. If the user asks a question in English, respond strictly in English. If they write in Hindi, respond in Hindi. If they write in Telugu, Tamil, Bengali, etc., respond in that language.
        Keep your advice actionable and focused on low-cost and organic alternatives where possible.
        """
        
        # Reconstruct history or send context directly
        context_prompt = f"{system_instruction}\n\nChat History:\n"
        for h in history[-10:]: # Keep last 10 messages for context
            role = "User" if h.get("role") == "user" else "Assistant"
            context_prompt += f"{role}: {h.get('parts', [''])[0]}\n"
        
        context_prompt += f"User: {message}\nAssistant:"
        
        response = model.generate_content(context_prompt)
        reply = response.text.strip()
        
        return jsonify({"reply": reply})
        
    except Exception as e:
        return jsonify({"error": f"Failed to get reply: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)

