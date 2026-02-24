from flask import Flask, render_template, request
import requests
from deep_translator import GoogleTranslator

app = Flask(__name__)

API_KEY = "du3c5wFmvCup7IbZj0vQiADFb0LzbEpi1goMRLeJ"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    food_input = request.form["food"]

    # Auto translate ke English
    try:
        translated_food = GoogleTranslator(source='auto', target='en').translate(food_input)
    except:
        translated_food = food_input

    # Cari makanan di USDA
    search_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    search_params = {
        "query": translated_food,
        "pageSize": 1,
        "api_key": API_KEY
    }

    response = requests.get(search_url, params=search_params)
    data = response.json()

    try:
        food_data = data["foods"][0]
        nutrients = food_data["foodNutrients"]

        calories = protein = fat = carbs = 0

        for n in nutrients:
            name = n["nutrientName"]

            if name == "Energy":
                calories = n["value"]
            elif name == "Protein":
                protein = n["value"]
            elif name == "Total lipid (fat)":
                fat = n["value"]
            elif name == "Carbohydrate, by difference":
                carbs = n["value"]

        # Status logic (per 100g biasanya)
        if carbs > 40:
            status = "Tinggi Karbohidrat (High Carbohydrate)"
            recommendation = "Kurangi karbo dan tambah protein."
        elif protein > 20:
            status = "Tinggi Protein (High Protein)"
            recommendation = "Baik untuk pembentukan otot."
        elif fat > 25:
            status = "Tinggi Lemak (High Fat)"
            recommendation = "Batasi makanan berlemak."
        else:
            status = "Seimbang (Balanced)"
            recommendation = "Pola makan cukup baik."

    except:
        calories = protein = fat = carbs = "-"
        status = "Data tidak ditemukan (Data not found)"
        recommendation = "Coba nama makanan lebih spesifik."

    return render_template(
        "index.html",
        food=food_input,
        calories=calories,
        protein=protein,
        fat=fat,
        carbs=carbs,
        status=status,
        recommendation=recommendation
    )

if __name__ == "__main__":
    app.run(debug=True)