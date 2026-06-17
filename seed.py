import os
from models import db, State, Crop, Soil, CropSoil, Disease, Chemical, NewsUpdate

def seed_database():
    # 1. Clear existing data
    db.session.query(Chemical).delete()
    db.session.query(Disease).delete()
    db.session.query(CropSoil).delete()
    db.session.query(Crop).delete()
    db.session.query(Soil).delete()
    db.session.query(State).delete()
    db.session.query(NewsUpdate).delete()
    db.session.commit()

    print("Cleared existing tables.")

    # 2. Seed States
    states_data = [
        {"state_name": "Andhra Pradesh", "climate": "Tropical Wet and Dry", "description": "Known as the Rice Bowl of India. Majorly dependent on monsoons and river canals for agriculture."},
        {"state_name": "Arunachal Pradesh", "climate": "Subtropical High Highland", "description": "Hilly terrain with shifting cultivation (Jhum) and organic farming of kiwi, ginger, and cardamom."},
        {"state_name": "Assam", "climate": "Tropical Wet", "description": "Famous for tea plantations, rich alluvial soil, and heavy rainfall. Cultivates rice, jute, and mustard."},
        {"state_name": "Bihar", "climate": "Humid Subtropical", "description": "Rich gangetic plains. High crop intensity with rice, wheat, maize, lentils, and litchi as key products."},
        {"state_name": "Chhattisgarh", "climate": "Tropical Wet and Dry", "description": "Often called the Rice Bowl of Central India. Heavily reliant on rainfed paddy farming and pulses."},
        {"state_name": "Goa", "climate": "Tropical Wet", "description": "Coastal region suitable for cashew, coconut, paddy, and tropical spices."},
        {"state_name": "Gujarat", "climate": "Semi-Arid / Arid", "description": "Leading producer of cotton, groundnut, and spices like cumin and fennel. Strong irrigation networks (Narmada canal)."},
        {"state_name": "Haryana", "climate": "Semi-Arid", "description": "Part of the Green Revolution hub. Highly mechanized wheat, paddy, and sugarcane farming with extensive canal irrigation."},
        {"state_name": "Himachal Pradesh", "climate": "Subtropical to Alpine", "description": "Ideal for horticulture, especially apples, stone fruits, off-season vegetables, and aromatic herbs."},
        {"state_name": "Jharkhand", "climate": "Tropical Wet and Dry", "description": "Mainly rainfed agriculture in plateau regions. Grows paddy, maize, pulses, and minor forest produce."},
        {"state_name": "Karnataka", "climate": "Tropical Semi-Arid to Wet", "description": "Diverse agro-climatic zones. Leading producer of coffee, ragi, maize, sunflower, and sugarcane."},
        {"state_name": "Kerala", "climate": "Tropical Wet", "description": "High rainfall coastal state. Specializes in plantation crops: rubber, coconut, black pepper, cardamom, and tea."},
        {"state_name": "Madhya Pradesh", "climate": "Tropical Wet and Dry", "description": "Known as the Soyabean and Pulse Bowl of India. Wheat is also a major crop grown in central plains."},
        {"state_name": "Maharashtra", "climate": "Tropical Wet and Dry / Semi-Arid", "description": "Major producer of sugarcane, cotton, soyabean, jowar, grapes, and Alphonso mangoes."},
        {"state_name": "Manipur", "climate": "Subtropical Humid", "description": "Terraced agriculture cultivating aromatic black rice (Chak-Hao), pineapples, and ginger."},
        {"state_name": "Meghalaya", "climate": "Subtropical Humid", "description": "Receives the highest rainfall globally. Famous for Lakadong turmeric, ginger, and pineapples."},
        {"state_name": "Mizoram", "climate": "Subtropical Humid", "description": "Hilly terrain practicing terraced and shifting agriculture. Grows passion fruit, turmeric, and bamboo shoots."},
        {"state_name": "Nagaland", "climate": "Subtropical Humid", "description": "Organic hilly agriculture. Cultivates Naga Mircha (King Chilli), maize, paddy, and local beans."},
        {"state_name": "Odisha", "climate": "Tropical Wet and Dry", "description": "Coastal plains suitable for rice, jute, coconut. Heavy monsoonal agriculture with frequent cyclone impacts."},
        {"state_name": "Punjab", "climate": "Semi-Arid to Subtropical", "description": "Granary of India. Intensive cultivation of wheat and basmati paddy utilizing tubewell and canal irrigation."},
        {"state_name": "Rajasthan", "climate": "Arid to Semi-Arid", "description": "Largest state. Cultivates drought-resistant crops like bajra, mustard, guar seed, and pulses using drip systems."},
        {"state_name": "Sikkim", "climate": "Montane Subtropical to Alpine", "description": "India's first fully organic state. Specializes in large cardamom, ginger, orchids, and temperate vegetables."},
        {"state_name": "Tamil Nadu", "climate": "Tropical Wet and Dry", "description": "Cultivates paddy, coconut, sugarcane, groundnut, and bananas. Strong winter monsoon influence (Northeast monsoon)."},
        {"state_name": "Telangana", "climate": "Semi-Arid", "description": "Major producer of cotton, paddy, maize, and chillies. Relies on lift irrigation schemes like Kaleshwaram."},
        {"state_name": "Tripura", "climate": "Tropical Wet", "description": "Cultivates pineapple, rubber, tea, and paddy in valley regions."},
        {"state_name": "Uttar Pradesh", "climate": "Humid Subtropical", "description": "Largest agricultural producer. Leading grower of sugarcane, wheat, potatoes, and mangoes in fertile gangetic plains."},
        {"state_name": "Uttarakhand", "climate": "Subtropical to Alpine", "description": "Mountain agriculture cultivating finger millet (ragi), barnyard millet, basmati rice, and organic herbs."},
        {"state_name": "West Bengal", "climate": "Tropical Wet", "description": "Highest producer of paddy and jute in India. Highly fertile Ganges-Brahmaputra delta region."},
        {"state_name": "Jammu & Kashmir", "climate": "Subtropical to Alpine", "description": "Famous for saffron cultivation, apples, walnuts, cherries, and almonds in alpine valleys."},
        {"state_name": "Puducherry", "climate": "Tropical Wet and Dry", "description": "Coastal agricultural pocket cultivating paddy, coconut, sugarcane, and bananas."}
    ]

    states = {}
    for item in states_data:
        state = State(state_name=item["state_name"], climate=item["climate"], description=item["description"])
        db.session.add(state)
        states[item["state_name"]] = state

    db.session.commit()
    print(f"Seeded {len(states_data)} States.")

    # 3. Seed Soils (20 Soil Types)
    soils_data = [
        {"soil_name": "Clayey Alluvial Soil", "characteristics": "Fine texture, high moisture retention, rich in humus, lime, and organic matter.", "ph_range": "6.5 - 7.8"},
        {"soil_name": "Sandy Alluvial Soil", "characteristics": "Coarse texture, well-drained, low water holding capacity, requires frequent irrigation.", "ph_range": "6.0 - 7.2"},
        {"soil_name": "Loamy Alluvial Soil", "characteristics": "Balanced sand, silt, and clay. Highly fertile, aerated, and easily tillable.", "ph_range": "6.5 - 7.5"},
        {"soil_name": "Deep Black Soil (Regur)", "characteristics": "High clay content, swells when wet, cracks when dry. Rich in iron, calcium, and magnesium.", "ph_range": "7.5 - 8.5"},
        {"soil_name": "Medium Black Soil", "characteristics": "Moderate depth and clay content, good moisture retention, suitable for dry farming.", "ph_range": "7.0 - 8.2"},
        {"soil_name": "Shallow Black Soil", "characteristics": "Thin layer on basaltic bedrock, rapid drainage, suitable for shallow-rooted crops.", "ph_range": "6.8 - 7.8"},
        {"soil_name": "Sandy Red Soil", "characteristics": "Porous, low nutrient retention, low organic matter, needs iron/phosphorus fertilizing.", "ph_range": "5.5 - 6.5"},
        {"soil_name": "Loamy Red Soil", "characteristics": "Good physical condition, moderately fertile, responsive to fertilizers and irrigation.", "ph_range": "6.0 - 7.0"},
        {"soil_name": "High Altitude Laterite Soil", "characteristics": "Acidic, highly leached, rich in iron and aluminum oxides, low in silica and potash.", "ph_range": "4.5 - 5.5"},
        {"soil_name": "Lowland Laterite Soil", "characteristics": "Moderate leaching, clayey-loam texture, responds well to organic manuring.", "ph_range": "5.0 - 6.0"},
        {"soil_name": "Sandy Desert Soil", "characteristics": "Very coarse, extremely low moisture retention, high soluble salts, low nitrogen content.", "ph_range": "7.5 - 9.0"},
        {"soil_name": "Saline Desert Soil", "characteristics": "Encrusted with salt, high electrical conductivity, unfit for crops without reclamation.", "ph_range": "8.0 - 9.5"},
        {"soil_name": "Acid Forest Soil", "characteristics": "Formed under forest cover, rich in leaf litter/organic matter, deficient in basic nutrients.", "ph_range": "5.0 - 6.0"},
        {"soil_name": "Humus-rich Forest Soil", "characteristics": "Rich dark color, high water retention, excellent for organic spice and tea farming.", "ph_range": "5.5 - 6.5"},
        {"soil_name": "Gravelly Mountain Soil", "characteristics": "Coarse stone-rich material, highly prone to erosion, suited for terraced horticulture.", "ph_range": "6.0 - 7.0"},
        {"soil_name": "Marshy Peaty Soil", "characteristics": "Heavy black clay, high acidity, waterlogged, rich in organic humus, found in coastal pockets.", "ph_range": "3.5 - 5.0"},
        {"soil_name": "Saline-Alkaline Soil (Usar)", "characteristics": "High sodium carbonate/chloride, sticky when wet, hard when dry, poor aeration.", "ph_range": "8.5 - 10.0"},
        {"soil_name": "Coastal Sandy Soil", "characteristics": "Pure sand, very high drainage, low fertility, ideal for coconuts and casuarina plantations.", "ph_range": "6.5 - 7.5"},
        {"soil_name": "Red and Yellow Soil", "characteristics": "Fine texture, yellow color when hydrated, deficient in nitrogen and phosphoric acid.", "ph_range": "5.5 - 7.0"},
        {"soil_name": "Lateritic Gravelly Soil", "characteristics": "Coarse gravelly texture, poor crop support, requires heavy organic matter inputs.", "ph_range": "5.0 - 6.2"}
    ]

    soils = {}
    for item in soils_data:
        soil = Soil(soil_name=item["soil_name"], characteristics=item["characteristics"], ph_range=item["ph_range"])
        db.session.add(soil)
        soils[item["soil_name"]] = soil

    db.session.commit()
    print(f"Seeded {len(soils_data)} Soil Types.")

    # 4. Seed Crops (50 crops)
    # Mapping structure for 50 crops:
    # (Crop Name, Scientific Name, Season, Water Req, Yield, State Name, Suitable Soil Names list, MSP)
    crops_raw = [
        ("Rice", "Oryza sativa", "Kharif", "High", "3.5 - 4.5 tons/hectare", ["West Bengal", "Andhra Pradesh", "Punjab", "Bihar", "Chhattisgarh", "Odisha", "Tamil Nadu", "Telangana", "Assam", "Haryana", "Uttar Pradesh", "Kerala", "Tripura", "Puducherry"], ["Clayey Alluvial Soil", "Loamy Alluvial Soil", "Marshy Peaty Soil"], "₹2,300 per quintal"),
        ("Wheat", "Triticum aestivum", "Rabi", "Medium", "3.0 - 4.0 tons/hectare", ["Punjab", "Haryana", "Uttar Pradesh", "Madhya Pradesh", "Rajasthan", "Bihar", "Gujarat", "Himachal Pradesh", "Uttarakhand", "Jammu & Kashmir"], ["Loamy Alluvial Soil", "Sandy Alluvial Soil", "Deep Black Soil (Regur)"], "₹2,275 per quintal"),
        ("Maize", "Zea mays", "Kharif/Rabi", "Medium", "2.5 - 3.5 tons/hectare", ["Karnataka", "Madhya Pradesh", "Bihar", "Tamil Nadu", "Telangana", "Andhra Pradesh", "Rajasthan", "Uttar Pradesh", "Himachal Pradesh"], ["Loamy Alluvial Soil", "Sandy Alluvial Soil", "Loamy Red Soil"], "₹2,225 per quintal"),
        ("Jowar (Sorghum)", "Sorghum bicolor", "Kharif/Rabi", "Low", "1.2 - 1.8 tons/hectare", ["Maharashtra", "Karnataka", "Madhya Pradesh", "Andhra Pradesh", "Telangana", "Tamil Nadu", "Rajasthan"], ["Deep Black Soil (Regur)", "Medium Black Soil", "Shallow Black Soil"], "₹3,371 per quintal"),
        ("Bajra (Pearl Millet)", "Pennisetum glaucum", "Kharif", "Very Low", "1.0 - 1.5 tons/hectare", ["Rajasthan", "Uttar Pradesh", "Haryana", "Gujarat", "Maharashtra"], ["Sandy Desert Soil", "Sandy Red Soil", "Sandy Alluvial Soil"], "₹2,625 per quintal"),
        ("Ragi (Finger Millet)", "Eleusine coracana", "Kharif", "Low", "1.5 - 2.2 tons/hectare", ["Karnataka", "Tamil Nadu", "Uttarakhand", "Maharashtra", "Andhra Pradesh", "Jharkhand", "Sikkim", "Himachal Pradesh"], ["Sandy Red Soil", "Loamy Red Soil", "Gravelly Mountain Soil"], "₹4,290 per quintal"),
        ("Barley", "Hordeum vulgare", "Rabi", "Low", "2.0 - 3.0 tons/hectare", ["Uttar Pradesh", "Rajasthan", "Madhya Pradesh", "Haryana", "Punjab", "Himachal Pradesh", "Jammu & Kashmir"], ["Sandy Alluvial Soil", "Loamy Alluvial Soil", "Saline Desert Soil"], "₹1,850 per quintal"),
        ("Tur (Arhar)", "Cajanus cajan", "Kharif", "Low", "0.8 - 1.2 tons/hectare", ["Madhya Pradesh", "Maharashtra", "Karnataka", "Uttar Pradesh", "Gujarat", "Jharkhand"], ["Medium Black Soil", "Loamy Red Soil", "Deep Black Soil (Regur)"], "₹7,550 per quintal"),
        ("Gram (Chickpea)", "Cicer arietinum", "Rabi", "Low", "1.0 - 1.5 tons/hectare", ["Madhya Pradesh", "Rajasthan", "Maharashtra", "Karnataka", "Uttar Pradesh", "Andhra Pradesh"], ["Medium Black Soil", "Deep Black Soil (Regur)", "Red and Yellow Soil"], "₹5,440 per quintal"),
        ("Urad (Black Gram)", "Vigna mungo", "Kharif/Rabi", "Low", "0.6 - 0.9 tons/hectare", ["Madhya Pradesh", "Uttar Pradesh", "Andhra Pradesh", "Maharashtra", "Tamil Nadu", "Jharkhand"], ["Medium Black Soil", "Loamy Alluvial Soil", "Loamy Red Soil"], "₹7,400 per quintal"),
        ("Mung (Green Gram)", "Vigna radiata", "Kharif/Rabi", "Low", "0.5 - 0.8 tons/hectare", ["Rajasthan", "Maharashtra", "Andhra Pradesh", "Gujarat", "Bihar", "Odisha"], ["Sandy Alluvial Soil", "Medium Black Soil", "Sandy Desert Soil"], "₹8,682 per quintal"),
        ("Masur (Lentil)", "Lens culinaris", "Rabi", "Low", "0.9 - 1.3 tons/hectare", ["Uttar Pradesh", "Madhya Pradesh", "Bihar", "West Bengal", "Rajasthan"], ["Loamy Alluvial Soil", "Clayey Alluvial Soil", "Red and Yellow Soil"], "₹6,425 per quintal"),
        ("Groundnut", "Arachis hypogaea", "Kharif", "Medium", "1.5 - 2.5 tons/hectare", ["Gujarat", "Andhra Pradesh", "Tamil Nadu", "Karnataka", "Rajasthan", "Maharashtra"], ["Sandy Red Soil", "Loamy Red Soil", "Medium Black Soil"], "₹6,783 per quintal"),
        ("Rapeseed & Mustard", "Brassica napus", "Rabi", "Low", "1.2 - 1.8 tons/hectare", ["Rajasthan", "Haryana", "Madhya Pradesh", "Uttar Pradesh", "West Bengal", "Assam"], ["Sandy Alluvial Soil", "Loamy Alluvial Soil", "Sandy Desert Soil"], "₹5,650 per quintal"),
        ("Soyabean", "Glycine max", "Kharif", "Medium", "1.8 - 2.4 tons/hectare", ["Madhya Pradesh", "Maharashtra", "Rajasthan", "Karnataka", "Telangana"], ["Deep Black Soil (Regur)", "Medium Black Soil", "Loamy Red Soil"], "₹4,892 per quintal"),
        ("Sunflower", "Helianthus annuus", "Kharif/Rabi", "Medium", "1.2 - 1.8 tons/hectare", ["Karnataka", "Andhra Pradesh", "Maharashtra", "Bihar", "Odisha"], ["Deep Black Soil (Regur)", "Medium Black Soil", "Loamy Alluvial Soil"], "₹7,280 per quintal"),
        ("Sesame (Til)", "Sesamum indicum", "Kharif/Rabi", "Low", "0.5 - 0.7 tons/hectare", ["Gujarat", "West Bengal", "Rajasthan", "Madhya Pradesh", "Tamil Nadu"], ["Sandy Alluvial Soil", "Sandy Red Soil", "Sandy Desert Soil"], "₹9,267 per quintal"),
        ("Nigerseed", "Guizotia abyssinica", "Kharif", "Low", "0.4 - 0.6 tons/hectare", ["Karnataka", "Madhya Pradesh", "Maharashtra", "Odisha", "Jharkhand"], ["Lateritic Gravelly Soil", "Loamy Red Soil", "Medium Black Soil"], "₹8,717 per quintal"),
        ("Safflower", "Carthamus tinctorius", "Rabi", "Very Low", "0.8 - 1.2 tons/hectare", ["Maharashtra", "Karnataka", "Andhra Pradesh", "Telangana"], ["Deep Black Soil (Regur)", "Medium Black Soil", "Saline Desert Soil"], "₹5,800 per quintal"),
        ("Castor Seed", "Ricinus communis", "Kharif", "Low", "1.5 - 2.0 tons/hectare", ["Gujarat", "Rajasthan", "Andhra Pradesh", "Telangana"], ["Sandy Alluvial Soil", "Sandy Red Soil", "Medium Black Soil"], "₹6,650 per quintal"),
        ("Cotton", "Gossypium hirsutum", "Kharif", "Medium", "2.0 - 3.0 bales/hectare", ["Gujarat", "Maharashtra", "Telangana", "Andhra Pradesh", "Karnataka", "Haryana", "Punjab", "Rajasthan"], ["Deep Black Soil (Regur)", "Medium Black Soil", "Red and Yellow Soil"], "₹7,121 per quintal"),
        ("Sugarcane", "Saccharum officinarum", "Annual", "High", "70 - 80 tons/hectare", ["Uttar Pradesh", "Maharashtra", "Karnataka", "Tamil Nadu", "Andhra Pradesh", "Gujarat", "Haryana", "Bihar", "Punjab"], ["Clayey Alluvial Soil", "Loamy Alluvial Soil", "Deep Black Soil (Regur)"], "₹340 per quintal (FRP)"),
        ("Jute", "Corchorus olitorius", "Kharif", "High", "2.2 - 2.8 tons/hectare", ["West Bengal", "Bihar", "Assam", "Odisha", "Tripura"], ["Clayey Alluvial Soil", "Loamy Alluvial Soil", "Marshy Peaty Soil"], "₹5,335 per quintal"),
        ("Mesta", "Hibiscus cannabinus", "Kharif", "Medium", "1.5 - 2.0 tons/hectare", ["Andhra Pradesh", "Odisha", "Bihar", "West Bengal", "Assam"], ["Sandy Alluvial Soil", "Loamy Red Soil", "Lateritic Gravelly Soil"], "₹3,862 per quintal"),
        ("Tea", "Camellia sinensis", "Perennial", "High", "1.8 - 2.5 tons/hectare", ["Assam", "West Bengal", "Kerala", "Tamil Nadu", "Himachal Pradesh", "Uttarakhand", "Sikkim", "Tripura"], ["Humus-rich Forest Soil", "High Altitude Laterite Soil", "Acid Forest Soil"], "N/A"),
        ("Coffee", "Coffea arabica", "Perennial", "High", "0.8 - 1.2 tons/hectare", ["Karnataka", "Kerala", "Tamil Nadu", "Andhra Pradesh"], ["Humus-rich Forest Soil", "High Altitude Laterite Soil", "Lowland Laterite Soil"], "N/A"),
        ("Rubber", "Hevea brasiliensis", "Perennial", "High", "1.5 - 2.0 tons/hectare", ["Kerala", "Tamil Nadu", "Tripura", "Karnataka", "Assam", "Meghalaya", "Goa"], ["Lowland Laterite Soil", "High Altitude Laterite Soil", "Loamy Red Soil"], "N/A"),
        ("Potato", "Solanum tuberosum", "Rabi", "Medium", "20 - 25 tons/hectare", ["Uttar Pradesh", "West Bengal", "Bihar", "Madhya Pradesh", "Punjab", "Gujarat"], ["Loamy Alluvial Soil", "Sandy Alluvial Soil", "Loamy Red Soil"], "N/A"),
        ("Tomato", "Solanum lycopersicum", "All Season", "Medium", "15 - 20 tons/hectare", ["Andhra Pradesh", "Karnataka", "Madhya Pradesh", "Maharashtra", "Odisha", "West Bengal"], ["Loamy Alluvial Soil", "Loamy Red Soil", "Medium Black Soil"], "N/A"),
        ("Onion", "Allium cepa", "Rabi/Kharif", "Medium", "12 - 18 tons/hectare", ["Maharashtra", "Karnataka", "Madhya Pradesh", "Gujarat", "Bihar", "Andhra Pradesh"], ["Loamy Alluvial Soil", "Medium Black Soil", "Sandy Alluvial Soil"], "N/A"),
        ("Brinjal", "Solanum melongena", "All Season", "Medium", "18 - 22 tons/hectare", ["West Bengal", "Odisha", "Bihar", "Gujarat", "Andhra Pradesh", "Chhattisgarh"], ["Loamy Alluvial Soil", "Loamy Red Soil", "Medium Black Soil"], "N/A"),
        ("Cabbage", "Brassica oleracea var. capitata", "Rabi", "Medium", "25 - 30 tons/hectare", ["West Bengal", "Odisha", "Bihar", "Assam", "Karnataka"], ["Loamy Alluvial Soil", "Clayey Alluvial Soil", "Loamy Red Soil"], "N/A"),
        ("Cauliflower", "Brassica oleracea var. botrytis", "Rabi", "Medium", "18 - 22 tons/hectare", ["Bihar", "West Bengal", "Uttar Pradesh", "Madhya Pradesh", "Haryana"], ["Loamy Alluvial Soil", "Clayey Alluvial Soil", "Loamy Red Soil"], "N/A"),
        ("Okra (Bhindi)", "Abelmoschus esculentus", "Kharif/Summer", "Medium", "8 - 12 tons/hectare", ["Andhra Pradesh", "West Bengal", "Bihar", "Gujarat", "Okra"], ["Loamy Alluvial Soil", "Loamy Red Soil", "Medium Black Soil"], "N/A"),
        ("Garlic", "Allium sativum", "Rabi", "Low", "8 - 10 tons/hectare", ["Madhya Pradesh", "Rajasthan", "Gujarat", "Uttar Pradesh", "Punjab"], ["Loamy Alluvial Soil", "Medium Black Soil", "Sandy Alluvial Soil"], "N/A"),
        ("Ginger", "Zingiber officinale", "Kharif", "Medium", "12 - 15 tons/hectare", ["Kerala", "Karnataka", "Meghalaya", "Arunachal Pradesh", "Mizoram", "Sikkim", "Himachal Pradesh", "Assam"], ["Humus-rich Forest Soil", "High Altitude Laterite Soil", "Loamy Red Soil"], "N/A"),
        ("Turmeric", "Curcuma longa", "Kharif", "Medium", "8 - 10 tons/hectare", ["Telangana", "Andhra Pradesh", "Tamil Nadu", "Karnataka", "Odisha", "West Bengal", "Meghalaya"], ["Loamy Alluvial Soil", "Loamy Red Soil", "High Altitude Laterite Soil"], "N/A"),
        ("Black Pepper", "Piper nigrum", "Perennial", "High", "0.3 - 0.5 tons/hectare", ["Kerala", "Karnataka", "Tamil Nadu", "Puducherry"], ["Humus-rich Forest Soil", "High Altitude Laterite Soil", "Lowland Laterite Soil"], "N/A"),
        ("Cardamom", "Elettaria cardamomum", "Perennial", "High", "0.2 - 0.3 tons/hectare", ["Kerala", "Karnataka", "Tamil Nadu", "Sikkim"], ["Humus-rich Forest Soil", "High Altitude Laterite Soil", "Acid Forest Soil"], "N/A"),
        ("Chilli", "Capsicum annuum", "Kharif/Rabi", "Low", "1.5 - 2.5 tons/hectare", ["Andhra Pradesh", "Telangana", "Karnataka", "Tamil Nadu", "Maharashtra", "West Bengal"], ["Medium Black Soil", "Loamy Red Soil", "Loamy Alluvial Soil"], "N/A"),
        ("Coriander", "Coriandrum sativum", "Rabi", "Low", "0.8 - 1.2 tons/hectare", ["Gujarat", "Madhya Pradesh", "Rajasthan", "Andhra Pradesh"], ["Loamy Alluvial Soil", "Medium Black Soil", "Sandy Alluvial Soil"], "N/A"),
        ("Cumin (Jeera)", "Cuminum cyminum", "Rabi", "Very Low", "0.5 - 0.7 tons/hectare", ["Gujarat", "Rajasthan"], ["Sandy Alluvial Soil", "Sandy Desert Soil", "Loamy Alluvial Soil"], "N/A"),
        ("Fennel (Saunf)", "Foeniculum vulgare", "Rabi", "Low", "1.0 - 1.5 tons/hectare", ["Gujarat", "Rajasthan", "Uttar Pradesh"], ["Sandy Alluvial Soil", "Loamy Alluvial Soil", "Medium Black Soil"], "N/A"),
        ("Fenugreek (Methi)", "Trigonella foenum-graecum", "Rabi", "Low", "1.2 - 1.6 tons/hectare", ["Rajasthan", "Gujarat", "Madhya Pradesh", "Uttar Pradesh"], ["Sandy Alluvial Soil", "Loamy Alluvial Soil", "Sandy Desert Soil"], "N/A"),
        ("Apple", "Malus domestica", "Perennial", "Medium", "10 - 12 tons/hectare", ["Jammu & Kashmir", "Himachal Pradesh", "Uttarakhand", "Sikkim", "Arunachal Pradesh"], ["Gravelly Mountain Soil", "Humus-rich Forest Soil", "Acid Forest Soil"], "N/A"),
        ("Mango", "Mangifera indica", "Perennial", "Medium", "8 - 12 tons/hectare", ["Uttar Pradesh", "Andhra Pradesh", "Karnataka", "Bihar", "Gujarat", "Maharashtra", "West Bengal"], ["Loamy Alluvial Soil", "Loamy Red Soil", "Medium Black Soil"], "N/A"),
        ("Banana", "Musa acuminata", "Annual", "High", "35 - 45 tons/hectare", ["Tamil Nadu", "Maharashtra", "Gujarat", "Andhra Pradesh", "Karnataka", "Kerala", "Puducherry"], ["Clayey Alluvial Soil", "Loamy Alluvial Soil", "Loamy Red Soil"], "N/A"),
        ("Citrus (Orange)", "Citrus reticulata", "Perennial", "Medium", "12 - 15 tons/hectare", ["Maharashtra", "Madhya Pradesh", "Assam", "Punjab", "Rajasthan", "Nagaland", "Manipur"], ["Medium Black Soil", "Loamy Alluvial Soil", "Loamy Red Soil"], "N/A"),
        ("Grapes", "Vitis vinifera", "Perennial", "Low", "20 - 25 tons/hectare", ["Maharashtra", "Karnataka", "Tamil Nadu", "Andhra Pradesh"], ["Medium Black Soil", "Loamy Alluvial Soil", "Loamy Red Soil"], "N/A"),
        ("Guava", "Psidium guajava", "Perennial", "Low", "12 - 18 tons/hectare", ["Uttar Pradesh", "Madhya Pradesh", "Bihar", "West Bengal", "Andhra Pradesh", "Chhattisgarh"], ["Loamy Alluvial Soil", "Sandy Alluvial Soil", "Loamy Red Soil"], "N/A")
    ]

    crops = {}
    for item in crops_raw:
        crop = Crop(
            crop_name=item[0],
            scientific_name=item[1],
            season=item[2],
            water_requirement=item[3],
            yield_val=item[4],
            image_url=f"/api/placeholder/400/300?crop={item[0].lower().replace(' ', '_')}",
            msp=item[7]
        )
        db.session.add(crop)
        
        # Handle crop state mapping
        state_names = item[5] if isinstance(item[5], list) else [item[5]]
        for st_name in state_names:
            if st_name in states:
                crop.states.append(states[st_name])
                
        # Handle crop soil mapping
        for soil_name in item[6]:
            soil_obj = soils[soil_name]
            crop.soils.append(soil_obj)
        crops[item[0]] = crop

    db.session.commit()
    print(f"Seeded {len(crops_raw)} Crops and mapped their Soils.")

    # 5. Seed Diseases (100 Diseases - exactly 2 per crop) and 6. Chemicals (100 Chemicals - 1 per disease)
    # We will build a list of diseases. Each item:
    # (Crop Name, Disease Name, Symptoms, Causes, Prevention, Chemical Name, Chemical Type, Dosage, Application Method, Safety Precautions)
    diseases_chemicals_raw = [
        # 1. Rice
        ("Rice", "Rice Blast", "Spindle-shaped spots on leaves with ash-colored centers and brown borders.", "Fungal infection by Magnaporthe oryzae.", "Avoid excess nitrogen, maintain clean water.", "Tricyclazole", "Fungicide", "0.6 g/litre", "Foliar Spray", "Wear gloves, mask, and safety goggles."),
        ("Rice", "Sheath Blight", "Oval greenish-grey lesions on leaf sheaths near the water line.", "Fungal pathogen Rhizoctonia solani.", "Deep plowing, crop rotation, and optimal spacing.", "Hexaconazole", "Fungicide", "2.0 ml/litre", "Foliar Spray", "Avoid contact with skin and inhalation of spray mist."),
        
        # 2. Wheat
        ("Wheat", "Stem Rust", "Elongated reddish-brown pustules on stems and leaves.", "Fungal infection by Puccinia graminis.", "Plant resistant varieties, early sowing.", "Tebuconazole", "Fungicide", "1.0 ml/litre", "Foliar Spray", "Do not spray against the wind direction."),
        ("Wheat", "Loose Smut", "Entire grain head turned into a black powdery mass of spores.", "Fungus Ustilago nuda.", "Use certified seed, treat seed before planting.", "Carboxin", "Fungicide", "2.5 g/kg seed", "Seed Treatment", "Wash hands thoroughly after handling treated seeds."),
        
        # 3. Maize
        ("Maize", "Maize Smut", "Galls or tumors on ears, tassels, leaves, and stalks containing black powder.", "Fungal pathogen Ustilago maydis.", "Remove and destroy galls before they rupture.", "Carbendazim", "Fungicide", "2.0 g/litre", "Foliar Spray", "Wear protective clothing; wash equipment after spray."),
        ("Maize", "Downy Mildew", "Chlorotic stripes on leaves, downy growth on leaf surfaces.", "Oomycete Peronosclerospora sorghi.", "Remove affected plants, use clean seeds.", "Metalaxyl", "Fungicide", "3.0 g/kg seed", "Seed Treatment", "Keep out of reach of children and domestic animals."),
        
        # 4. Jowar (Sorghum)
        ("Jowar (Sorghum)", "Grain Smut", "Individual grains replaced by greyish-white smut sori.", "Fungus Sporisorium sorghi.", "Seed dressing with fungicides.", "Sulphur Dust", "Fungicide", "3.0 g/kg seed", "Seed Treatment", "Avoid breathing dust; wear dust mask."),
        ("Jowar (Sorghum)", "Ergot", "Sweet sticky pinkish liquid oozes from spikelets, later turning hard black.", "Fungus Claviceps sorghi.", "Destroy infected heads, plow deeply.", "Propiconazole", "Fungicide", "1.0 ml/litre", "Foliar Spray", "Highly toxic to aquatic life. Do not contaminate water bodies."),
        
        # 5. Bajra (Pearl Millet)
        ("Bajra (Pearl Millet)", "Green Ear Disease", "Floral parts transformed into leafy structures, green tufts.", "Oomycete Sclerospora graminicola.", "Clean seeds, rotation with non-cereal crops.", "Metalaxyl-M", "Fungicide", "2.0 g/litre", "Soil Drench", "Avoid skin contact; wash affected area with soap immediately."),
        ("Bajra (Pearl Millet)", "Ergot of Bajra", "Creamy sticky fluid dripping from spikes, grain replaced by dark sclerotia.", "Fungus Claviceps fusiformis.", "Salt water seed floatation to remove sclerotia.", "Mancozeb", "Fungicide", "2.5 g/litre", "Foliar Spray", "Do not eat, drink, or smoke during application."),
        
        # 6. Ragi (Finger Millet)
        ("Ragi (Finger Millet)", "Blast of Ragi", "Spindle-shaped lesions on leaves and blackening of neck region.", "Fungus Pyricularia grisea.", "Balance nitrogen application, seed treat.", "Kitazin", "Fungicide", "1.0 ml/litre", "Foliar Spray", "Store in original container in cool dry place."),
        ("Ragi (Finger Millet)", "Smut", "Grains replaced by large greenish-black galls.", "Fungus Melanopsichium eleusinis.", "Clean seed usage, crop rotation.", "Thiram", "Fungicide", "2.5 g/kg seed", "Seed Treatment", "Avoid skin exposure; wear chemical resistant apron."),
        
        # 7. Barley
        ("Barley", "Powdery Mildew", "White to grey powdery patches on leaves and stems.", "Fungus Blumeria graminis.", "Plant resistant cultivars, avoid overcrowding.", "Dinocap", "Fungicide", "1.0 ml/litre", "Foliar Spray", "Toxic to bees. Apply in late evening when bees are not active."),
        ("Barley", "Stripe Rust", "Yellow pustules arranged in long stripes on leaf blades.", "Fungus Puccinia striiformis.", "Avoid over-irrigation, apply balanced potash.", "Azoxystrobin", "Fungicide", "1.0 ml/litre", "Foliar Spray", "Use face shield and protective boots."),
        
        # 8. Tur (Arhar)
        ("Tur (Arhar)", "Fusarium Wilt of Pigeonpea", "Gradual yellowing and wilting of plants, brown streaks under bark.", "Soil-borne fungus Fusarium udum.", "Three-year crop rotation, intercropping with Sorghum.", "Trichoderma viride", "Bio-Fungicide", "10.0 g/litre", "Soil Drench", "Safe organic compound, but wash hands after use."),
        ("Tur (Arhar)", "Sterility Mosaic", "Leaves turn small, pale green with light yellow mosaic patches; no flowers.", "Pigeonpea sterility mosaic virus, spread by eriophyid mites.", "Uproot infected plants early, spray acaricides.", "Spiromesifen", "Acaricide", "1.0 ml/litre", "Foliar Spray", "Harmful if swallowed; induce vomiting if ingested accidentally."),
        
        # 9. Gram (Chickpea)
        ("Gram (Chickpea)", "Ascochyta Blight", "Circular dark spots on leaves with black dot-like pycnidia.", "Fungus Ascochyta rabiei.", "Burn infected residues, wider row spacing.", "Chlorothalonil", "Fungicide", "2.0 g/litre", "Foliar Spray", "Do not inhale dust or spray mist."),
        ("Gram (Chickpea)", "Fusarium Wilt of Gram", "Drooping and yellowing of leaves followed by complete wilting.", "Fungus Fusarium oxysporum f. sp. ciceris.", "Sow resistant cultivars, deep summer plowing.", "Captan", "Fungicide", "3.0 g/kg seed", "Seed Treatment", "Keep away from foodstuff, empty feed bags."),
        
        # 10. Urad (Black Gram)
        ("Urad (Black Gram)", "Powdery Mildew of Urad", "White powdery growth starting on lower leaves and spreading.", "Fungus Erysiphe polygoni.", "Early planting, sulfur dusting.", "Wettable Sulphur", "Fungicide", "3.0 g/litre", "Foliar Spray", "Avoid contact with eyes; flush with water if exposed."),
        ("Urad (Black Gram)", "Yellow Mosaic of Urad", "Bright yellow patches on leaves, reduced leaf size, stunted growth.", "Mungbean yellow mosaic virus, spread by whitefly.", "Grow resistant varieties, control whiteflies.", "Thiamethoxam", "Insecticide", "0.5 g/litre", "Foliar Spray", "Do not spray near beehives or flowering weeds."),
        
        # 11. Mung (Green Gram)
        ("Mung (Green Gram)", "Cercospora Leaf Spot", "Small brown spots with purple margins on leaves.", "Fungus Cercospora canescens.", "Clean cultivation, remove crop debris.", "Zineb", "Fungicide", "2.0 g/litre", "Foliar Spray", "Wash hands and face with soap and water after spray."),
        ("Mung (Green Gram)", "Yellow Mosaic of Mung", "Diffuse yellow spots on leaf lamina that merge to make leaf yellow.", "Mungbean yellow mosaic virus.", "Use yellow sticky traps, spray systemic insecticides.", "Acetamiprid", "Insecticide", "0.4 g/litre", "Foliar Spray", "Wash protective gear before reuse."),
        
        # 12. Masur (Lentil)
        ("Masur (Lentil)", "Rust of Lentil", "Small, brown, circular pustules on leaves, petioles, and stems.", "Fungus Uromyces viciae-fabae.", "Early sowing, destroy wild hosts.", "Penconazole", "Fungicide", "1.0 ml/litre", "Foliar Spray", "Highly toxic to fish; do not drain wash water in streams."),
        ("Masur (Lentil)", "Lentil Wilt", "Sudden wilting of seedlings or adult plants in patches.", "Fungus Fusarium oxysporum.", "Deep plowing, seed treatment with bioagents.", "Trichoderma harzianum", "Bio-Fungicide", "5.0 g/kg seed", "Seed Treatment", "Organic formulation; avoid eye irritation."),
        
        # 13. Groundnut
        ("Groundnut", "Tikka Leaf Spot", "Circular dark brown spots surrounded by a bright yellow halo.", "Fungus Cercospora arachidicola.", "Deep bury of organic residues, crop rotation.", "Tebuconazole + Trifloxystrobin", "Fungicide", "1.0 g/litre", "Foliar Spray", "Wear full body coverall, chemical resistant gloves."),
        ("Groundnut", "Rust of Groundnut", "Orange-colored pustules on the lower leaf surface.", "Fungus Puccinia arachidis.", "Avoid sowing in infected soils, clean field margins.", "Chlorothalonil", "Fungicide", "2.0 g/litre", "Foliar Spray", "Do not apply during high wind speeds."),
        
        # 14. Rapeseed & Mustard
        ("Rapeseed & Mustard", "Alternaria Blight", "Concentric dark spots on leaves, stems, and siliquae.", "Fungus Alternaria brassicae.", "Early planting, destroy crop residues.", "Iprodione", "Fungicide", "2.0 g/litre", "Foliar Spray", "Store away from heat sources and open flames."),
        ("Rapeseed & Mustard", "White Rust", "White creamy pustules on lower leaves, hyper-trophy of flowers.", "Oomycete Albugo candida.", "Destroy mustard weed hosts, seed treatment.", "Metalaxyl + Mancozeb", "Fungicide", "2.5 g/litre", "Foliar Spray", "Do not smoke, eat, or drink while spraying."),
        
        # 15. Soyabean
        ("Soyabean", "Soybean Rust", "Small tan to dark brown lesions on the underside of leaves.", "Fungus Phakopsora pachyrhizi.", "Avoid high planting density, monitor early.", "Pyraclostrobin", "Fungicide", "1.5 g/litre", "Foliar Spray", "Avoid dermal contact; wash skin thoroughly if exposed."),
        ("Soyabean", "Yellow Mosaic of Soybean", "Bright yellow mosaic patches on leaves, pods are small and deformed.", "Soybean yellow mosaic virus.", "Eradicate weed hosts, spray insect vector controls.", "Imidacloprid", "Insecticide", "0.5 ml/litre", "Foliar Spray", "Dangerous to bees; apply early morning or evening."),
        
        # 16. Sunflower
        ("Sunflower", "Sunflower Rust", "Dark brown, dusty pustules on leaves, petioles, and bracts.", "Fungus Puccinia helianthi.", "Plow stubble deep, use tolerant hybrids.", "Difenoconazole", "Fungicide", "1.0 ml/litre", "Foliar Spray", "Wash contaminated clothing before reuse."),
        ("Sunflower", "Alternaria Leaf Spot", "Dark brown circular spots with concentric rings on leaves.", "Fungus Alternaria helianthi.", "Use clean certified seeds, optimal spacing.", "Mancozeb", "Fungicide", "2.5 g/litre", "Foliar Spray", "Wear goggles and long sleeves."),
        
        # 17. Sesame (Til)
        ("Sesame (Til)", "Phyllody", "Floral parts transform into green leafy structures; sterility.", "Phytoplasma vector-transmitted by leafhopper.", "Uproot infected plants, spray vector controls.", "Dimethoate", "Insecticide", "2.0 ml/litre", "Foliar Spray", "Ensure protective mask is worn to avoid fumes."),
        ("Sesame (Til)", "Sesame Leaf Spot", "Angled dark brown spots on leaf margins and centers.", "Fungus Cercospora sesami.", "Destroy previous crop residues, treat seeds.", "Carbendazim", "Fungicide", "2.0 g/litre", "Foliar Spray", "Avoid contact with open wounds."),
        
        # 18. Nigerseed
        ("Nigerseed", "Niger Leaf Spot", "Small brownish black circular lesions on leaf blades.", "Fungus Alternaria brassicicola.", "Crop rotation, seed treatment.", "Carbendazim + Mancozeb", "Fungicide", "2.0 g/litre", "Foliar Spray", "Do not inhale spray dust; use filter mask."),
        ("Nigerseed", "Powdery Mildew of Niger", "Dull white powdery coating on leaves and stems.", "Fungus Oidium sp.", "Early sowing, avoid excess shade.", "Sulphur 80% WP", "Fungicide", "3.0 g/litre", "Foliar Spray", "Keep livestock away from treated area for 48 hours."),
        
        # 19. Safflower
        ("Safflower", "Safflower Alternaria Leaf Spot", "Dark brown spots with yellow halos on leaf blades.", "Fungus Alternaria carthami.", "Plant healthy seed, avoid overwatering.", "Mancozeb", "Fungicide", "2.5 g/litre", "Foliar Spray", "Dispose of packaging material safely after use."),
        ("Safflower", "Safflower Wilt", "Leaves turn yellow, dry up, and the plant wilts.", "Fungus Fusarium oxysporum f. sp. carthami.", "Grow resistant varieties, solarize soil.", "Trichoderma formulation", "Bio-Fungicide", "10.0 g/litre", "Soil Drench", "Eco-friendly agent, standard washing required."),
        
        # 20. Castor Seed
        ("Castor Seed", "Castor Seedling Blight", "Water-soaked circular lesions on cotyledonary leaves.", "Fungus Phytophthora parasitica var. nicotianae.", "Improve drainage, seed dressing.", "Metalaxyl", "Fungicide", "3.0 g/kg seed", "Seed Treatment", "Wash hands after dressing seeds."),
        ("Castor Seed", "Castor Wilt", "Drooping of leaves, drying up of branches, stem blackening.", "Fungus Fusarium oxysporum f. sp. ricini.", "Drench soil, grow wilt-tolerant castor hybrids.", "Carbendazim", "Fungicide", "2.0 g/litre", "Soil Drench", "Avoid contact with skin; use rubber boots."),
        
        # 21. Cotton
        ("Cotton", "Cotton Boll Rot", "Bolls turn dark brown, fail to open, and get covered with mold.", "Fungal/Bacterial complex.", "Apply proper spacing, clear lower leaves.", "Copper Oxychloride", "Fungicide", "3.0 g/litre", "Foliar Spray", "Store in dry place away from food supplies."),
        ("Cotton", "Bacterial Blight of Cotton", "Angular water-soaked leaf spots, black arm on stems.", "Bacterium Xanthomonas citri pv. malvacearum.", "Acid-delint seed, spray antibiotics.", "Streptomycin sulphate", "Bactericide", "0.2 g/litre", "Foliar Spray", "Antibiotic compound. Use strict protective gear."),
        
        # 22. Sugarcane
        ("Sugarcane", "Red Rot", "Reddening of internal pith tissues with white transverse patches.", "Fungus Colletotrichum falcatum.", "Use healthy setts, practice crop rotation.", "Carbendazim", "Fungicide", "1.5 g/litre", "Sett Treatment", "Soak setts with gloves and apron on."),
        ("Sugarcane", "Sugarcane Smut", "Long, whip-like dusty black structure emerging from the shoot apex.", "Fungus Sporisorium scitamineum.", "Rogue out smutted whips, avoid ratoon crop.", "Propiconazole", "Fungicide", "1.0 ml/litre", "Foliar Spray", "Ensure protective eyewear is worn."),
        
        # 23. Jute
        ("Jute", "Stem Rot of Jute", "Brown spots on stems which turn black, causing stem breakage.", "Fungus Macrophomina phaseolina.", "Seed treatment, add potash fertilizer.", "Carbendazim", "Fungicide", "2.0 g/litre", "Foliar Spray", "Wear rubber gloves during preparation."),
        ("Jute", "Anthracnose of Jute", "Sunken spots on stem with black dot-like acervuli.", "Fungus Colletotrichum corchori.", "Clean field debris, balance NPK.", "Mancozeb", "Fungicide", "2.5 g/litre", "Foliar Spray", "Wash face and hands after application."),
        
        # 24. Mesta
        ("Mesta", "Stem Rot of Mesta", "Brownish black lesions on stems leading to plant death.", "Fungus Macrophomina phaseolina.", "Clean farming, avoid waterlogging.", "Carbendazim", "Fungicide", "2.0 g/kg seed", "Seed Treatment", "Do not inhale dust or touch eyes."),
        ("Mesta", "Mesta Leaf Spot", "Circular greyish brown spots on leaves causing defoliation.", "Fungus Cercospora sp.", "Clear previous weeds, spray fungicides.", "Zineb", "Fungicide", "2.0 g/litre", "Foliar Spray", "Wash hands thoroughly with soap."),
        
        # 25. Tea
        ("Tea", "Blister Blight", "Translucent oily spots on leaves turning into white blister-like structures.", "Fungus Exobasidium vexans.", "Pruning for aeration, apply copper spray.", "Copper Oxychloride + Hexaconazole", "Fungicide", "2.0 g/litre", "Foliar Spray", "Highly toxic to fish; keep out of ponds."),
        ("Tea", "Red Rust of Tea", "Orange-yellow velvety spots on stems and leaves.", "Algal parasite Cephaleuros virescens.", "Provide shade trees, improve drainage.", "Copper Oxychloride", "Algicide", "3.0 g/litre", "Foliar Spray", "Store in a cool dry well-ventilated space."),
        
        # 26. Coffee
        ("Coffee", "Coffee Leaf Rust", "Powdery orange spots on the lower leaf surface, causing defoliation.", "Fungus Hemileia vastatrix.", "Apply copper spray before monsoon.", "Copper Oxychloride", "Fungicide", "3.0 g/litre", "Foliar Spray", "Do not spray during mid-day heat."),
        ("Coffee", "Black Rot of Coffee", "Leaves turn black, rot, and hang by thread-like mycelial strands.", "Fungus Koleroga noxia.", "Prune lower branches, clear weeds.", "Bordeaux Mixture 1%", "Fungicide", "10.0 g/litre", "Foliar Spray", "Wear mask and protective clothing."),
        
        # 27. Rubber
        ("Rubber", "Abnormal Leaf Fall", "Water-soaked lesions on petioles, leaves fall while still green.", "Fungus Phytophthora meadii.", "Prophylactic crown spray before monsoon.", "Copper Oxychloride in oil", "Fungicide", "4.0 kg/hectare", "Aerial Spray", "Ensure protective suit and mask are worn."),
        ("Rubber", "Pink Disease", "Cobwebby pink growth on bark, bark cracks, and bleeds latex.", "Fungus Erythricium salmonicolor.", "Apply copper paste to affected nodes.", "Bordeaux Paste", "Fungicide", "Brush on bark", "Direct Application", "Wear rubber gloves during hand brush."),
        
        # 28. Potato
        ("Potato", "Late Blight of Potato", "Water-soaked dark lesions on leaf tips/margins, white mold underneath.", "Oomycete Phytophthora infestans.", "Use certified tubers, destroy volunteers.", "Metalaxyl + Mancozeb", "Fungicide", "2.5 g/litre", "Foliar Spray", "Do not spray within 14 days of harvest."),
        ("Potato", "Early Blight of Potato", "Dark spots with concentric target-board rings on leaves.", "Fungus Alternaria solani.", "Clean crop rotations, destroy debris.", "Chlorothalonil", "Fungicide", "2.0 g/litre", "Foliar Spray", "Avoid inhalation of spray droplets."),
        
        # 29. Tomato
        ("Tomato", "Early Blight of Tomato", "Concentric rings on leaves and black sunken spots on fruit stem end.", "Fungus Alternaria solani.", "Drip irrigation to avoid wet leaves, spray.", "Mancozeb", "Fungicide", "2.5 g/litre", "Foliar Spray", "Keep children and pets away from area."),
        ("Tomato", "Tomato Leaf Curl", "Leaves curl upwards, turn yellow, plant becomes dwarfed.", "Tomato leaf curl virus, spread by whitefly.", "Nursery nylon mesh nets, systemic spray.", "Imidacloprid", "Insecticide", "0.5 ml/litre", "Foliar Spray", "Highly toxic to bees. Avoid spraying flowers."),
        
        # 30. Onion
        ("Onion", "Purple Blotch of Onion", "Water-soaked spots turning purple with concentric zones.", "Fungus Alternaria porri.", "Good drainage, seed dressing, foliar spray.", "Mancozeb + Tricyclazole", "Fungicide", "2.0 g/litre", "Foliar Spray", "Wear gloves, safety boots, and goggles."),
        ("Onion", "Downy Mildew of Onion", "Fuzzy pale violet mold on leaves, causing collapse of leaf tips.", "Oomycete Peronospora destructor.", "Destroy weed hosts, avoid sprinkler irrigation.", "Metalaxyl", "Fungicide", "2.0 g/litre", "Foliar Spray", "Do not feed treated onion waste to livestock."),
        
        # 31. Brinjal
        ("Brinjal", "Phomopsis Blight", "Brown circular spots on leaves, dry rot on fruit.", "Fungus Phomopsis vexans.", "Use disease-free seed, crop rotation.", "Carbendazim", "Fungicide", "2.0 g/litre", "Foliar Spray", "Wash hands well before eating."),
        ("Brinjal", "Little Leaf of Brinjal", "Extremely small leaves, yellowing, no fruit forms.", "Phytoplasma vector-transmitted by leafhopper.", "Uproot infected plants immediately, spray vector control.", "Dimethoate", "Insecticide", "2.0 ml/litre", "Foliar Spray", "Use safety mask; toxic compound."),
        
        # 32. Cabbage
        ("Cabbage", "Black Rot of Cabbage", "V-shaped yellow lesions on leaf margins, veins turn black.", "Bacterium Xanthomonas campestris pv. campestris.", "Hot water seed treatment, sanitation.", "Streptocycline", "Bactericide", "0.1 g/litre", "Foliar Spray", "Use face shield and chemical gloves."),
        ("Cabbage", "Club Root", "Stunted growth, club-like swelling of roots.", "Protozoa Plasmodiophora brassicae.", "Apply lime to raise soil pH to 7.2 or above.", "Hydrated Lime", "Soil Conditioner", "1000 kg/ha", "Soil Incorporation", "Corrosive to skin; wear protective gloves."),
        
        # 33. Cauliflower
        ("Cauliflower", "Cauliflower Downy Mildew", "Yellow spots on upper leaf surfaces, white fluffy growth on underside.", "Oomycete Hyaloperonospora brassicae.", "Destroy weeds, proper field spacing.", "Metalaxyl + Mancozeb", "Fungicide", "2.5 g/litre", "Foliar Spray", "Do not inhale mist; wash clothes."),
        ("Cauliflower", "Cauliflower Black Rot", "Stunting, leaf yellowing, blackening of curd stalks.", "Bacterium Xanthomonas campestris.", "Crop rotation, healthy nursery seeds.", "Copper Oxychloride + Streptocycline", "Bactericide/Fungicide", "3.0 g + 0.1 g/litre", "Foliar Spray", "Wash sprayer after use; toxic to fish."),
        
        # 34. Okra (Bhindi)
        ("Okra (Bhindi)", "Yellow Vein Mosaic of Okra", "Veins turn bright yellow, leaves yellow completely, small green-yellow pods.", "Bendy yellow vein mosaic virus, spread by whitefly.", "Grow resistant hybrids, spray vector controls.", "Acetamiprid", "Insecticide", "0.4 g/litre", "Foliar Spray", "Avoid contact with skin and eyes."),
        ("Okra (Bhindi)", "Okra Powdery Mildew", "Greyish white powdery coating on upper surface of leaves.", "Fungus Erysiphe cichoracearum.", "Dusting sulfur, spray fungicides.", "Dinop", "Fungicide", "1.0 ml/litre", "Foliar Spray", "Avoid spraying in windy conditions."),
        
        # 35. Garlic
        ("Garlic", "Garlic Purple Blotch", "Sunken spots with purple centers on leaves and flower stalks.", "Fungus Alternaria porri.", "Clean cloves before sowing, optimal spacing.", "Mancozeb", "Fungicide", "2.5 g/litre", "Foliar Spray", "Wear protective mask and clothing."),
        ("Garlic", "Garlic Downy Mildew", "White fuzzy growth on leaves, leaves droop and dry.", "Oomycete Peronospora destructor.", "Ensure proper soil drainage.", "Metalaxyl", "Fungicide", "2.0 g/litre", "Foliar Spray", "Do not store near food or animal feed."),
        
        # 36. Ginger
        ("Ginger", "Soft Rot of Ginger", "Water-soaking at collar region, leaves turn yellow and drop off.", "Oomycete Pythium myriotylum.", "Use healthy seed rhizomes, raised beds.", "Metalaxyl-M", "Fungicide", "2.5 g/litre", "Rhizome treatment", "Soak rhizomes with heavy gloves on."),
        ("Ginger", "Ginger Yellows", "Stunting, yellowing of margins, rhizomes dry up.", "Fungus Fusarium oxysporum f. sp. zingiberi.", "Solarize soil, use bioagents.", "Trichoderma harzianum", "Bio-Fungicide", "10.0 g/kg rhizome", "Rhizome coating", "Eco-friendly, wash face after handling."),
        
        # 37. Turmeric
        ("Turmeric", "Rhizome Rot of Turmeric", "Progressive drying of leaves, rhizomes decay into a foul-smelling mass.", "Oomycete Pythium aphanidermatum.", "Good drainage, seed selection.", "Metalaxyl + Mancozeb", "Fungicide", "3.0 g/litre", "Soil Drench", "Wear protective boots and gloves."),
        ("Turmeric", "Turmeric Leaf Spot", "Oval brown spots with grey centers on leaves.", "Fungus Colletotrichum capsici.", "Treat seeds, clear crop debris.", "Carbendazim", "Fungicide", "2.0 g/litre", "Foliar Spray", "Wash skin thoroughly if exposed to chemical."),
        
        # 38. Black Pepper
        ("Black Pepper", "Quick Wilt of Pepper", "Sudden death of vines, leaves drop off within days.", "Oomycete Phytophthora capsici.", "Clean basin, spray copper compound.", "Bordeaux Mixture 1%", "Fungicide", "10.0 g/litre", "Foliar Spray", "Prepare mixture in earthen or wooden vessel."),
        ("Black Pepper", "Foot Rot", "Rotting of collar region, peeling of bark, black discharge.", "Oomycete Phytophthora capsici.", "Avoid water logging around pepper supports.", "Metalaxyl", "Fungicide", "2.5 g/litre", "Soil Drench", "Store away from heat and open flames."),
        
        # 39. Cardamom
        ("Cardamom", "Capsule Rot of Cardamom", "Water-soaked lesions on leaves and rotting of capsules (clump rot).", "Oomycete Phytophthora meadii.", "Remove affected shoots, clear canopy.", "Copper Oxychloride", "Fungicide", "3.0 g/litre", "Foliar Spray", "Do not dump leftover spray in streams."),
        ("Cardamom", "Katte Disease of Cardamom", "Continuous pale green stripes on leaves, stunting.", "Cardamom mosaic virus, transmitted by banana aphid.", "Grow tissue culture clones, remove infected clumps.", "Dimethoate", "Insecticide", "2.0 ml/litre", "Foliar Spray", "Use safety mask; do not breathe mist."),
        
        # 40. Chilli
        ("Chilli", "Anthracnose of Chilli", "Sunken circular dark spots on fruits with black dot-like acervuli.", "Fungus Colletotrichum capsici.", "Clean seeds, spray during pod formation.", "Azoxystrobin", "Fungicide", "1.0 ml/litre", "Foliar Spray", "Use face shield and protective apron."),
        ("Chilli", "Chilli Leaf Curl", "Leaves curl upwards, crinkle, and turn small.", "Chilli leaf curl virus, spread by thrips/whiteflies.", "Use nursery nylon nets, systemic insect sprays.", "Imidacloprid", "Insecticide", "0.5 ml/litre", "Foliar Spray", "Dangerous to honey bees; spray late evening."),
        
        # 41. Coriander
        ("Coriander", "Stem Gall of Coriander", "Tumor-like swellings on stem, leaves, and pedicels.", "Fungus Protomyces macrosporus.", "Use clean seed, rotation with non-umbelliferous crops.", "Hexaconazole", "Fungicide", "1.5 ml/litre", "Foliar Spray", "Wash hands and face with soap after spray."),
        ("Coriander", "Coriander Powdery Mildew", "White powdery dust covering leaves and flowers.", "Fungus Erysiphe polygoni.", "Sulfur dusting at early flower stage.", "Wettable Sulphur", "Fungicide", "3.0 g/litre", "Foliar Spray", "Avoid contact with eyes; wear safety goggles."),
        
        # 42. Cumin (Jeera)
        ("Cumin (Jeera)", "Cumin Wilt", "Drooping of tips, complete drying of plants in patches.", "Fungus Fusarium oxysporum f. sp. cumini.", "Use certified seed, treat seed.", "Carbendazim", "Fungicide", "2.5 g/kg seed", "Seed Treatment", "Keep out of reach of children."),
        ("Cumin (Jeera)", "Cumin Powdery Mildew", "White powdery coating on foliage, seed does not develop.", "Fungus Erysiphe polygoni.", "Early morning sulfur dusting.", "Sulphur Dust", "Fungicide", "25 kg/hectare", "Dusting", "Wear dust mask; do not apply during high wind."),
        
        # 43. Fennel (Saunf)
        ("Fennel (Saunf)", "Ramularia Blight", "Greyish brown spots on leaves, stems, and flower heads.", "Fungus Ramularia foeniculi.", "Remove crop residues, spray fungicides.", "Mancozeb", "Fungicide", "2.5 g/litre", "Foliar Spray", "Avoid skin exposure; wear long pants."),
        ("Fennel (Saunf)", "Fennel Powdery Mildew", "Powdery white patches on leaf surface.", "Fungus Leveillula taurica.", "Proper field sanitation.", "Propiconazole", "Fungicide", "1.0 ml/litre", "Foliar Spray", "Toxic to aquatic life; handle carefully."),
        
        # 44. Fenugreek (Methi)
        ("Fenugreek (Methi)", "Fenugreek Downy Mildew", "Yellow spots on leaves with violet-grey downy growth underneath.", "Oomycete Peronospora trigonellae.", "Keep area clean, proper drainage.", "Metalaxyl + Mancozeb", "Fungicide", "2.5 g/litre", "Foliar Spray", "Do not eat or drink during application."),
        ("Fenugreek (Methi)", "Fenugreek Powdery Mildew", "White patches on both leaf surfaces.", "Fungus Erysiphe polygoni.", "Balanced irrigation.", "Dinocap", "Fungicide", "1.0 ml/litre", "Foliar Spray", "Wash spray tools thoroughly after work."),
        
        # 45. Apple
        ("Apple", "Apple Scab", "Olive green to black velvety spots on leaves and scabby lesions on fruits.", "Fungus Venturia inaequalis.", "Rake and burn fallen leaves, prune trees.", "Flusilazole", "Fungicide", "0.2 ml/litre", "Foliar Spray", "Wear protective coverall and chemical boots."),
        ("Apple", "Apple Powdery Mildew", "White powdery coating on buds, leaves, and young twigs.", "Fungus Podosphaera leucotricha.", "Prune infected shoots in winter.", "Wettable Sulphur", "Fungicide", "2.5 g/litre", "Foliar Spray", "Do not apply during high temperatures."),
        
        # 46. Mango
        ("Mango", "Mango Powdery Mildew", "White powdery growth on inflorescence and young leaves, causing flower drop.", "Fungus Oidium mangiferae.", "Spray sulfur before flowering.", "Wettable Sulphur", "Fungicide", "3.0 g/litre", "Foliar Spray", "Ensure eye protection is worn during spray."),
        ("Mango", "Mango Anthracnose", "Black leaf spots, blossom blight, black spots on mango fruit.", "Fungus Colletotrichum gloeosporioides.", "Prune dead twigs, spray during fruit set.", "Carbendazim + Mancozeb", "Fungicide", "2.0 g/litre", "Foliar Spray", "Wash hands and face with soap before eating."),
        
        # 47. Banana
        ("Banana", "Panama Wilt of Banana", "Yellowing of leaf margins, leaf collapse, split pseudostem.", "Soil-borne fungus Fusarium oxysporum f. sp. cubense.", "Use disease-free suckers, apply biocontrol.", "Trichoderma viride", "Bio-Fungicide", "10.0 g/plant", "Rhizome treatment", "Safe organic agent. Wash hands after use."),
        ("Banana", "Sigatoka Leaf Spot", "Narrow yellowish brown streaks parallel to veins on leaves.", "Fungus Mycosphaerella musicola.", "Remove infected leaves, improve drainage.", "Propiconazole + Mineral Oil", "Fungicide", "1.0 ml + 10 ml/l", "Foliar Spray", "Wear respiratory protection; avoid oil mist."),
        
        # 48. Citrus (Orange)
        ("Citrus (Orange)", "Citrus Canker", "Raised corky spots on leaves, stems, and fruit surrounded by yellow halos.", "Bacterium Xanthomonas citri.", "Prune infected twigs, spray copper compound.", "Copper Oxychloride + Streptomycin", "Bactericide/Fungicide", "3.0 g + 0.1 g/litre", "Foliar Spray", "Store away from heat and food items."),
        ("Citrus (Orange)", "Citrus Gummosis", "Exudation of sap/gum from bark, cracks on bark near ground.", "Oomycete Phytophthora citrophthora.", "Avoid water accumulation around tree trunks.", "Metalaxyl paste", "Fungicide", "Brush on bark", "Direct Application", "Wear rubber gloves during hand brush."),
        
        # 49. Grapes
        ("Grapes", "Grape Downy Mildew", "Yellow oily spots on upper leaves, white downy growth underneath.", "Oomycete Plasmopara viticola.", "Keep vines pruned for air, spray before monsoon.", "Metalaxyl + Mancozeb", "Fungicide", "2.5 g/litre", "Foliar Spray", "Toxic to bees. Avoid drift to flowering weeds."),
        ("Grapes", "Grape Powdery Mildew", "Ash-colored powdery growth on leaves and berries.", "Fungus Uncinula necator.", "Pruning for sunshine.", "Sulphur WP", "Fungicide", "3.0 g/litre", "Foliar Spray", "Avoid contact with eyes; flush immediately."),
        
        # 50. Guava
        ("Guava", "Guava Wilt", "Yellowing and shedding of leaves, death of branches.", "Soil fungus Fusarium oxysporum f. sp. psidii.", "Grow resistant rootstocks, soil solarization.", "Trichoderma harzianum", "Bio-Fungicide", "20.0 g/litre", "Soil Drench", "Safe organic culture."),
        ("Guava", "Guava Anthracnose", "Sunken spots with dark margins on fruits.", "Fungus Colletotrichum gloeosporioides.", "Clean cultivation, remove rotten fruits.", "Mancozeb", "Fungicide", "2.5 g/litre", "Foliar Spray", "Wash face and hands after application.")
    ]

    diseases = {}
    for item in diseases_chemicals_raw:
        crop_obj = crops.get(item[0])
        if not crop_obj:
            print(f"Error: Crop {item[0]} not found in seeded crops.")
            continue
        
        disease = Disease(
            disease_name=item[1],
            symptoms=item[2],
            causes=item[3],
            prevention=item[4],
            crop_id=crop_obj.id,
            image_url=f"/api/placeholder/400/300?disease={item[1].lower().replace(' ', '_')}"
        )
        db.session.add(disease)
        db.session.flush() # Gain the ID immediately for chemicals

        chemical = Chemical(
            chemical_name=item[5],
            chemical_type=item[6],
            dosage=item[7],
            application_method=item[8],
            safety_precautions=item[9],
            disease_id=disease.id
        )
        db.session.add(chemical)
        diseases[item[1]] = disease

    db.session.commit()
    print(f"Seeded {len(diseases_chemicals_raw)} Diseases and their corresponding {len(diseases_chemicals_raw)} Chemicals.")

    # 6. Seed News Updates (5 realistic articles)
    news_data = [
        {
            "title": "PM-KISAN 17th Installment of ₹2,000 Transferred to 9.2 Crore Farmers",
            "content": "The Prime Minister has released the 17th installment of the Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) scheme. Over ₹20,000 crores have been directly transferred to the bank accounts of more than 9.2 crore eligible farmers across India. Farmers can check their status on the official PM-KISAN portal using their Aadhaar card. This assistance helps farmers prepare for Kharif sowing.",
            "category": "Scheme",
            "published_date": "2026-06-15",
            "source": "Ministry of Agriculture & Farmers Welfare",
            "image_url": "https://images.unsplash.com/photo-1593113598332-cd288d649433?auto=format&fit=crop&q=80&w=800"
        },
        {
            "title": "IMD Issues Heavy Rainfall Advisory for Maharashtra, Telangana, and Andhra Pradesh",
            "content": "The India Meteorological Department (IMD) has issued an orange alert for several agricultural zones in Western and Southern India. A low-pressure area over the Bay of Bengal is expected to bring widespread heavy monsoon rains. Farmers are advised to delay sowing of cotton and soyabean in waterlogged fields and ensure proper drainage channels in orchards.",
            "category": "Weather",
            "published_date": "2026-06-16",
            "source": "India Meteorological Department (IMD)",
            "image_url": "https://images.unsplash.com/photo-1534274988757-a28bf1a57c17?auto=format&fit=crop&q=80&w=800"
        },
        {
            "title": "Cotton Prices Surge by 8% in Western Indian Mandis Amid Export Demand",
            "content": "Cotton prices have surged in major mandis of Gujarat and Maharashtra, driven by strong export orders. The average price per quintal reached ₹7,800, which is significantly above the MSP of ₹7,121. Cotton sowing has dipped slightly due to delayed rainfall, driving spot market values higher. Analysts advise farmers to sell in tranches to maximize gains.",
            "category": "Market Trend",
            "published_date": "2026-06-14",
            "source": "AgriMarket Intelligence India",
            "image_url": "https://images.unsplash.com/photo-1509099836639-18ba1795216d?auto=format&fit=crop&q=80&w=800"
        },
        {
            "title": "Central Government Announces 50% Subsidy on Agricultural Drones",
            "content": "To promote smart and precision agriculture, the government has announced a 50% financial subsidy (up to ₹5 lakhs) for agricultural cooperatives, FPOs, and custom hiring centers to purchase drone setups. Drones reduce chemical usage and protect farmers from direct contact with pesticides during spraying operations. Applications can be submitted through state portals.",
            "category": "Technology",
            "published_date": "2026-06-12",
            "source": "Department of Agriculture",
            "image_url": "https://images.unsplash.com/photo-1508614589041-895b88991e3e?auto=format&fit=crop&q=80&w=800"
        },
        {
            "title": "How to Correctly Apply Jeevamrutha Organic Fertilizer for Soil Health",
            "content": "Agricultural scientists have published a guide for preparation and application of Jeevamrutha. Made from local cow dung, cow urine, pulse flour, and virgin soil, Jeevamrutha stimulates microbial activity, enhancing crop nutrient absorption. Apply 200 liters per acre twice a month alongside standard irrigation channels for best organic yield results.",
            "category": "General",
            "published_date": "2026-06-10",
            "source": "ICAR Advisory Bulletin",
            "image_url": "https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?auto=format&fit=crop&q=80&w=800"
        }
    ]

    for item in news_data:
        news = NewsUpdate(
            title=item["title"],
            content=item["content"],
            category=item["category"],
            published_date=item["published_date"],
            source=item["source"],
            image_url=item["image_url"]
        )
        db.session.add(news)
    
    db.session.commit()
    print(f"Seeded {len(news_data)} News Updates.")
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    # Standalone script run
    import sys
    from flask import Flask
    from models import db
    
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///agriculture.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        seed_database()
