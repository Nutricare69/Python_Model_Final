# AI-Driven Personalized Nutrition & Meal Recommendation System

An enterprise-grade, full-stack microservices application that orchestrates machine learning analysis, metabolic target calculation, and cultural/medical heuristic mapping to generate completely customized, macro-balanced nutrition plans.

---

## 🏗️ System Architecture Overview

The platform uses a split-microservices topology designed to decouple computational processing from storage and UI layers:

[ React Client ] ──(Axios HTTP)──> [ Node.js Gateway / MongoDB ]
│
(JSON Payload Gateway)
▼
[ Python FastAPI Compute Engine ]

1. **Frontend Layer (React):** A premium UI dashboard implemented with Tailwind CSS, Lucide Icons, and Framer Motion fluid hardware-accelerated tracking loops.
2. **Gateway API Layer (Node.js & Express):** Routes inbound execution parameters to the ML stack, handles data aggregation, and persists calculations to MongoDB.
3. **Core AI/Compute Engine (Python FastAPI):** A stateless in-memory processing cluster that runs dynamic vector masking, metabolic target calculations, multi-objective score rankings, and dynamic recency decay matrices.

---

## 🚀 Getting Started

### 📋 Prerequisites

- Node.js (v18.x or higher)
- Python (v3.10.x or higher)
- MongoDB Instance (Local or Atlas Cloud Cluster)

### 🛠️ Step 1: Clone and Environment Setup

Clone the repository to your local directory setup:

````bash
git clone [https://github.com/your-username/nutricare-core.git](https://github.com/your-username/nutricare-core.git)
cd nutricare-core

Create a .env configuration file inside your Node Backend directory:

PORT=5000
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/nutricare
ML_SERVER_URL=http://localhost:8000
JWT_SECRET=your_system_auth_token_secret

🛠️ Step 2: Microservices Installation & Initialization
Open three concurrent terminal windows to boot the execution stacks:

Terminal 1: Python FastAPI Compute Cluster

cd backend-python
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000


Terminal 2: Node.js Orchestration Gateway
cd backend-node
npm install
npm run dev

Terminal 3: React Frontend Dashboard
cd frontend-client
npm install
npm run dev

🛣️ API Route Documentation

### 🟢 Node.js Orchestration Gateway

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/generate/ml-response-generate` | Aggregates client profile parameters, forwards payloads to FastAPI, saves calculations to MongoDB, and compiles clean outputs. |
| GET | `/api/generate/all-plans` | Fetches historical generated dietary snapshot documents from MongoDB assigned to the authenticated user. |
| POST | `/api/user/profile` | Creates or updates user profile with personal health data and preferences. |
| GET | `/api/user/profile` | Retrieves the current user's complete profile information. |

**Sample Request Body for Meal Generation:**
```json
{
  "weight": 76.9,
  "height": 172.0,
  "goal": "Weight Loss",
  "food_preference": "Non-Veg",
  "gender": "Male",
  "days": 7,
  "region": "East",
  "state": "West Bengal",
  "medical_conditions": [],
  "allergies": [],
  "activity_level": "Moderate"
}
````

**Sample Response:**

```json
{
  "status": "success",
  "plan_id": "64a2f8e3c1b2d4e5f6g7h8i9",
  "profileSnapshot": {
    "bmi": 25.9,
    "bmi_category": "Overweight",
    "tdee": 2450
  },
  "daily_targets": {
    "target_calories": 1960,
    "target_protein": 140,
    "target_fat": 65,
    "target_carbs": 245
  },
  "days": [...]
}
```

### 🔵 Python FastAPI Compute Engine

| Method | Endpoint                  | Description                                                                                                                                          |
| ------ | ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| POST   | `/api/meal-plan/generate` | Accepts structured metabolic profile parameters, applies safety filtering matrices, scores food datasets, and executes attribute rotation pipelines. |
| POST   | `/api/bmi/calculate`      | Computes BMI and category based on height and weight inputs.                                                                                         |
| POST   | `/api/calorie/calculate`  | Generates BMR and TDEE values from metabolic parameters and activity levels.                                                                         |
| GET    | `/api/food/all`           | Retrieves complete food database with nutritional information.                                                                                       |
| POST   | `/api/food/filter`        | Filters foods based on allergies, medical conditions, and preferences.                                                                               |

**FastAPI Request Format:**

```json
{
  "weight_kg": 76.9,
  "height_cm": 172.0,
  "age": 30,
  "gender": "Male",
  "goal": "Weight Loss",
  "food_preference": "Non-Veg",
  "days": 7,
  "region": "East",
  "state": "West Bengal",
  "medical_conditions": [],
  "allergies": [],
  "activity_level": "Moderate"
}
```

**FastAPI Response Format:**

```json
{
  "status": "success",
  "bmi": 25.9,
  "bmi_category": "Overweight",
  "bmr": 1680,
  "tdee": 2450,
  "meal_plan": {
    "daily_targets": {
      "calories": 1960,
      "protein": 140,
      "fat": 65,
      "carbs": 245
    },
    "days": [...]
  }
}
```

🧠 Core Service Layers (Python Engine Architecture)
The stateless Python compute framework is orchestrated using highly modular single-responsibility service patterns:

[ app.api.meal_plans ]
│
▼
[ app.services.meal_generator ]
│
├─► [ app.services.bmi_service ] ──────► (Calculates BMI + Category)
├─► [ app.services.calorie_service ] ──► (Generates BMR / TDEE Targets)
├─► [ app.services.allergy_service ] ──► (Hard Vector Matrix Masking)
├─► [ app.services.disease_service ] ──► (Pathology Contraint Masks)
└─► [ app.services.ranking_service ] ──► (Heuristic Composite Scoring)

🎛️ MealGenerator (app/services/meal_generator.py)
Acts as the central execution manager for payload compilation, operating completely in memory:

Input Adapter Pass: Maps variables sent from Node.js (e.g., translating weight_kg attributes to core parameters).

Selection Optimization Guard: Implements a strict 1 Grain Base + 1 Accompaniment pairing restriction inside select_food_combination() to prevent unpractical match errors (like serving two liquid dishes together or two dry roti discs without a side).

Dynamic Recency Decay Engine: Tracks protein attributes (Fish, Chicken, Egg) consumed during the current simulated day iteration and injects a temporary -45 point suppression penalty into those categories for the next 24-hour cycle. This forces underrepresented items like chicken to cleanly rotate to the top of the selection stack.

📊 RankingService (app/services/ranking_service.py)
Computes a dynamic suitability matrix from 0.0 to 100.0 for every safe row in your database:

Geographic Affinity Boost: Matches row attributes against selected parameters (state and region), injecting score multipliers for localized options (e.g., prioritizing West Bengal items when East India maps are active).

Goal Bounding Gates: Dynamically drops or rewards foods based on nutrient density maps. If a user sets their parameters to "Weight Loss," foods containing high saturated fats take a dedicated -30 point penalty check, and dishes matching cheat strings (like "Biryani") receive a -50 point deduction gate to block calorie-dense options from monopolizing high scores.

Pathology Compatibility Matching: Maps parameters against clinical guidelines, altering row suitability thresholds for specialized flags like Diabetes or Hypertension.

🛡️ Defensive Engineering Filters
AllergyService & DiseaseService: Run structural boundary filtering via pandas masking blocks before any heuristic calculations run. If a food item contains an active allergen array token, it is completely removed from memory.

Cosmetic Masking Adapter: Cleanses text encodings during serialization, stripping character rendering anomalies (like â) and mapping raw empty string inputs ("") into clean, queryable "Global" or "All States" presentation tokens before data reaches MongoDB or the React UI components.

💾 Database Document Topology (Mongoose / MongoDB)
Calculated snap records are tracked within MongoDB under a highly nested document frame to protect data isolation over time:

JavaScript
const nutriPlanSchema = new mongoose.Schema({
user: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
planNumber: { type: Number, required: true },

profileSnapshot: {
age: Number,
weight: Number,
height: Number,
gender: String,
goal: String,
food_preference: String,
medical_conditions: [String],
allergies: [String],
activity_level: String,
bmi: Number,
bmi_category: String, // Calculated by Python Layer
tdee: Number,
days: Number,
region: String, // Injected Fallback Token
state: String // Injected Fallback Token
},

daily_targets: {
target_calories: Number,
target_protein: Number,
target_fat: Number,
target_carbs: Number
},

days: [
{
dayNumber: Number,
meals: [
{
mealType: { type: String, enum: ["Breakfast", "Lunch", "Dinner"] },
foods: [
{
name: String,
calories: Number,
protein: Number,
fat: Number,
carbs: Number
}
]
}
]
}
],
createdAt: { type: Date, default: Date.now }
});
🛠️ Verification & Troubleshooting
If your technical review panel notices issues or if requests drop down the integration bridge, verify these checkpoints:

The Trailing Slash Rule: FastAPI requires rigid trailing slash patterns. Ensure Node.js calls http://localhost:8000/api/meal-plan/generate/ with the trailing slash included to bypass 404 router exceptions.

Pydantic Validation Guard exceptions: If you modify input parameters on the UI side, update both UserProfileSchema and PythonMLMealPlanResponseSchema inside the Python layer. If keys don't match, Uvicorn will trigger a 422 Unprocessable Entity or a ResponseValidationError traceback block.

Database Population Check: If meal cards appear blank on your client screens, verify the days property inside your MongoDB document. If it reads Array (empty), check your Python adapter return statement to confirm data properties are named exactly "days", aligning with the Express structural destructuring lines.
