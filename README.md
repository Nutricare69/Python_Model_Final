# AI-Driven Personalized Nutrition & Meal Recommendation System

An end-to-end personalized nutrition platform that creates structured meal plans using a React client, a Node.js orchestration layer, a Python FastAPI compute service, and MongoDB storage.

The system is built to:

- calculate BMI, BMR, and TDEE
- generate daily calorie and macro targets
- recommend meals based on user goals and preferences
- filter unsafe food options using allergies and medical conditions
- rank foods using regional, nutritional, and plan-based rules
- save generated plans for later viewing and comparison

---

## Table of Contents

- Overview
- Key Features
- Tech Stack
- System Architecture
- Project Structure
- Installation
- Environment Variables
- API Reference
- Data Flow
- Data Models
- Core Services
- Input Rules
- Troubleshooting
- Future Improvements

---

## Overview

This project accepts user health and preference inputs and converts them into personalized nutrition outputs.

Typical inputs include:

- weight and height
- age and gender
- fitness or weight goal
- food preference
- activity level
- region and state
- medical conditions
- allergies
- number of days required

The FastAPI service computes the nutrition values, the Node.js server manages requests and persistence, and the frontend presents the final meal plan in a user-friendly format.

---

## Key Features

### Nutrition Calculation

- BMI calculation
- BMI category classification
- BMR calculation
- TDEE estimation
- macro target generation

### Meal Personalization

- goal-based meal planning
- vegetarian and non-vegetarian support
- region and state-aware ranking
- allergy filtering
- medical-condition filtering
- day-wise meal rotation

### Platform Features

- modular microservices design
- FastAPI-based computation
- Node.js gateway for orchestration
- MongoDB persistence for generated plans
- React dashboard for plan display

---

## Tech Stack

### Frontend

- React
- Tailwind CSS
- Framer Motion
- Lucide Icons

### Backend

- Node.js
- Express
- Python
- FastAPI

### Database

- MongoDB

### Supporting Libraries

- pandas
- mongoose
- pydantic

---

## System Architecture

```text
[ React Client ]
        |
        | Axios / HTTP
        v
[ Node.js Gateway ] -----> [ MongoDB ]
        |
        | JSON request forwarding
        v
[ Python FastAPI Compute Engine ]
```

### Layer Responsibilities

#### React Client

- collects profile inputs
- sends meal generation requests
- displays the generated meal plan

#### Node.js Gateway

- receives requests from the frontend
- validates payload structure
- forwards data to FastAPI
- stores completed plans in MongoDB

#### Python FastAPI Compute Engine

- performs metabolic calculations
- filters unsafe foods
- ranks meal options
- builds the final meal plan output

#### MongoDB

- stores user profiles
- stores generated meal plans
- keeps plan history for reuse and review

---

## Project Structure

```text
root
├── backend-node
├── backend-python
├── frontend-client
└── README.md
```

---

## Installation

### Prerequisites

- Node.js v18 or later
- Python 3.10 or later
- MongoDB local instance or cloud cluster

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/nutricare-core.git
cd nutricare-core
```

### 2. Configure Environment Variables

Create a `.env` file in the Node.js backend folder.

```env
PORT=5000
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/nutricare
ML_SERVER_URL=http://localhost:8000
```

### 3. Start the Python FastAPI Service

```bash
cd backend-python
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 4. Start the Node.js Backend

```bash
cd backend-node
npm install
npm run dev
```

### 5. Start the Frontend

```bash
cd frontend-client
npm install
npm run dev
```

---

## Environment Variables

### Node.js Backend

| Variable | Purpose |
|---|---|
| `PORT` | Port for the gateway server |
| `MONGO_URI` | MongoDB connection string |
| `ML_SERVER_URL` | FastAPI service URL |

If additional local settings are needed for the Python layer, keep them in a separate service config file.

---

## API Reference

### Node.js Gateway

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/generate/ml-response-generate` | Generates a meal plan by forwarding the request to FastAPI and storing the result |
| GET | `/api/generate/all-plans` | Returns saved meal plans |
| POST | `/api/user/profile` | Creates or updates a user profile |
| GET | `/api/user/profile` | Returns the current profile data |

### Python FastAPI Service

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/meal-plan/generate` | Generates a full meal plan from profile data |
| POST | `/api/bmi/calculate` | Calculates BMI and BMI category |
| POST | `/api/calorie/calculate` | Calculates BMR and TDEE |
| GET | `/api/food/all` | Returns the food catalog |
| POST | `/api/food/filter` | Filters food based on preferences and restrictions |

---

## Request and Response Examples

### Meal Generation Request

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
```

### Meal Generation Response

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
  "days": []
}
```

### FastAPI Request Example

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

### FastAPI Response Example

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
    "days": []
  }
}
```

---

## Data Flow

1. The user submits nutrition preferences from the frontend.
2. The Node.js gateway receives and forwards the payload to FastAPI.
3. FastAPI calculates BMI, calorie targets, and meal composition.
4. Unsafe or incompatible foods are filtered out.
5. Suitable foods are ranked and assembled into daily meal plans.
6. The final result is returned to Node.js.
7. Node.js stores the plan in MongoDB and sends the response to the frontend.

---

## Data Models

### Meal Plan Document

```javascript
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
    bmi_category: String,
    tdee: Number,
    days: Number,
    region: String,
    state: String
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
```

---

## Core Services

### Meal Generator

- normalizes input fields
- coordinates meal assembly
- ensures each day has a structured output
- applies meal selection rules

### BMI Service

- calculates BMI from weight and height
- classifies BMI into a category

### Calorie Service

- estimates BMR
- derives TDEE from activity level
- prepares daily targets

### Allergy Service

- removes foods containing allergen matches
- prevents unsafe recommendations

### Disease Service

- applies medical-condition-based exclusions
- limits foods that conflict with health rules

### Ranking Service

- scores food rows based on region, preference, and goal
- promotes foods with better fit for the target profile
- reduces scores for unsuitable items

---

## Input Rules

- `weight` and `height` must be numeric
- `days` should be a positive integer
- `medical_conditions` must be an array
- `allergies` must be an array
- `goal` should match supported goal labels
- `food_preference` should match the supported diet type
- `region` and `state` should be passed consistently

---

## Troubleshooting

### FastAPI Endpoint Not Found

Verify the endpoint path and ensure the gateway is calling the correct route.

### Validation Errors

If the API returns a 422 error, check that the JSON keys and data types match the schema expected by the backend.

### Empty Meal Output

If the UI renders empty meal cards, confirm that the response includes a populated `days` array.

### MongoDB Connection Problems

- verify the MongoDB URI
- confirm the database server is running
- check credentials and network access

### Python Service Startup Problems

- activate the virtual environment
- install dependencies
- confirm the FastAPI app module path is correct

---

## Future Improvements

- grocery list generation
- weekly meal analytics
- PDF export for meal plans
- ingredient-level replacement suggestions
- multilingual support
- nutrition history charts
- pantry-based recommendations

---

## Notes

- Keep field names consistent across frontend, Node.js, Python, and MongoDB.
- Maintain consistent units for weight, height, and nutrition values.
- Use the same response shape in every service layer to avoid serialization issues.
