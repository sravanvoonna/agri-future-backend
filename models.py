from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class State(db.Model):
    __tablename__ = 'states'
    
    id = db.Column(db.Integer, primary_key=True)
    state_name = db.Column(db.String(100), nullable=False, unique=True)
    climate = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Relationships
    crops = db.relationship('Crop', secondary='crop_states', back_populates='states')

    def to_dict(self):
        return {
            "id": self.id,
            "state_name": self.state_name,
            "climate": self.climate,
            "description": self.description
        }


class Crop(db.Model):
    __tablename__ = 'crops'
    
    id = db.Column(db.Integer, primary_key=True)
    crop_name = db.Column(db.String(100), nullable=False)
    scientific_name = db.Column(db.String(100), nullable=False)
    season = db.Column(db.String(50), nullable=False)
    water_requirement = db.Column(db.String(50), nullable=False)
    yield_val = db.Column(db.String(100), name="yield", nullable=False) # Maps to yield in DB
    image_url = db.Column(db.String(255), nullable=True)
    msp = db.Column(db.String(100), nullable=True)
    
    # Relationships
    diseases = db.relationship('Disease', backref='crop', lazy=True, cascade="all, delete-orphan")
    soils = db.relationship('Soil', secondary='crop_soils', back_populates='crops')
    states = db.relationship('State', secondary='crop_states', back_populates='crops')

    def to_dict(self):
        return {
            "id": self.id,
            "crop_name": self.crop_name,
            "scientific_name": self.scientific_name,
            "season": self.season,
            "water_requirement": self.water_requirement,
            "yield": self.yield_val,
            "msp": self.msp,
            "state_id": self.states[0].id if self.states else None,
            "state_name": self.states[0].state_name if self.states else None,
            "state_ids": [s.id for s in self.states],
            "state_names": [s.state_name for s in self.states],
            "image_url": self.image_url,
            "soils": [s.soil_name for s in self.soils]
        }


class Soil(db.Model):
    __tablename__ = 'soils'
    
    id = db.Column(db.Integer, primary_key=True)
    soil_name = db.Column(db.String(100), nullable=False, unique=True)
    characteristics = db.Column(db.Text, nullable=False)
    ph_range = db.Column(db.String(50), nullable=False)
    
    # Relationships
    crops = db.relationship('Crop', secondary='crop_soils', back_populates='soils')

    def to_dict(self):
        return {
            "id": self.id,
            "soil_name": self.soil_name,
            "characteristics": self.characteristics,
            "ph_range": self.ph_range,
            "suitable_crops": [c.crop_name for c in self.crops]
        }


class CropSoil(db.Model):
    __tablename__ = 'crop_soils'
    
    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crops.id', ondelete="CASCADE"), nullable=False)
    soil_id = db.Column(db.Integer, db.ForeignKey('soils.id', ondelete="CASCADE"), nullable=False)


class CropState(db.Model):
    __tablename__ = 'crop_states'
    
    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crops.id', ondelete="CASCADE"), nullable=False)
    state_id = db.Column(db.Integer, db.ForeignKey('states.id', ondelete="CASCADE"), nullable=False)


class Disease(db.Model):
    __tablename__ = 'diseases'
    
    id = db.Column(db.Integer, primary_key=True)
    disease_name = db.Column(db.String(100), nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    causes = db.Column(db.Text, nullable=False)
    prevention = db.Column(db.Text, nullable=False)
    crop_id = db.Column(db.Integer, db.ForeignKey('crops.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    
    # Relationships
    chemicals = db.relationship('Chemical', backref='disease', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "disease_name": self.disease_name,
            "symptoms": self.symptoms,
            "causes": self.causes,
            "prevention": self.prevention,
            "crop_id": self.crop_id,
            "crop_name": self.crop.crop_name if self.crop else None,
            "image_url": self.image_url
        }


class Chemical(db.Model):
    __tablename__ = 'chemicals'
    
    id = db.Column(db.Integer, primary_key=True)
    chemical_name = db.Column(db.String(100), nullable=False)
    chemical_type = db.Column(db.String(50), nullable=False)  # Fungicide, Pesticide, Herbicide, etc.
    dosage = db.Column(db.String(100), nullable=False)
    application_method = db.Column(db.String(100), nullable=False)
    safety_precautions = db.Column(db.Text, nullable=False)
    disease_id = db.Column(db.Integer, db.ForeignKey('diseases.id'), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "chemical_name": self.chemical_name,
            "chemical_type": self.chemical_type,
            "dosage": self.dosage,
            "application_method": self.application_method,
            "safety_precautions": self.safety_precautions,
            "disease_id": self.disease_id,
            "disease_name": self.disease.disease_name if self.disease else None,
            "crop_name": self.disease.crop.crop_name if self.disease and self.disease.crop else None
        }


class NewsUpdate(db.Model):
    __tablename__ = 'news_updates'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, unique=True)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Scheme, Weather, Market Trend, Technology, General
    published_date = db.Column(db.String(50), nullable=False)
    source = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "published_date": self.published_date,
            "source": self.source,
            "image_url": self.image_url
        }


# ─────────────────────────────────────────────────────────────────────────────
# USER AUTHENTICATION MODELS
# ─────────────────────────────────────────────────────────────────────────────

from datetime import datetime as _dt

class User(db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    # At least one of email / phone must be provided (enforced in app logic)
    email         = db.Column(db.String(150), nullable=True, unique=True)
    phone         = db.Column(db.String(20),  nullable=True, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at    = db.Column(db.DateTime, default=_dt.utcnow)

    activities = db.relationship(
        'UserActivity', backref='user', lazy=True, cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            "id":         self.id,
            "name":       self.name,
            "email":      self.email,
            "phone":      self.phone,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class UserActivity(db.Model):
    __tablename__ = 'user_activities'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action_type = db.Column(db.String(80),  nullable=False)   # e.g. "crop_viewed"
    description = db.Column(db.String(255), nullable=False)   # human-readable label
    extra       = db.Column(db.Text, nullable=True)           # JSON blob with extra info
    created_at  = db.Column(db.DateTime, default=_dt.utcnow)

    def to_dict(self):
        return {
            "id":          self.id,
            "action_type": self.action_type,
            "description": self.description,
            "extra":       self.extra,
            "created_at":  self.created_at.isoformat() if self.created_at else None
        }
