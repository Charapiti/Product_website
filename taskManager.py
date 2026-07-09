from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request, redirect


#set up the connection to the database and the collection we will be using
client = MongoClient("mongodb://localhost:27017/")
db = client["Products_db"]
students = db["Products"]
print("Connected to MongoDB\n")


# flask to run the web server and render the html pages
app = Flask(__name__, template_folder="templates")

#  routes for the web server
@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("Project_main_page.html")

@app.route("/add_product", methods=["POST", "GET"])
def add_product_page():
    return render_template("add_product.html")

# -----------------------------------------------------------  API routes
@app.route("/api/products", methods=["GET"])
def getting_products():
    products = list(students.find({}, {"_id": 0}))
    return jsonify(products)

@app.route("/api/products_info", methods=["GET"])
def products_info():
    pipeline = [
        {"$match": {}},
        {"$group": {"_id": None,
                "unique_products": {"$sum": 1},
                "max_price": {"$max": "$Price"},
                "min_price": {"$min": "$Price"}
            }}
    ]

    return jsonify(list(students.aggregate(pipeline))[0])


@app.route("/api/update_stock/<name>/<change>", methods=["POST", "GET"])
def update_stock(name, change):
    change = int(change)
    temp = students.find_one({"Name": name})

    if int(temp["Stock"]) + change < 0:
        return jsonify({"error": "Stock cannot be negative"}), 400
    else:
        result = students.update_one(
            {"Name": name},
            {"$inc": {"Stock": change}}
        )
        return jsonify({"message": "Stock updated successfully"}), 200
    
@app.route("/api/delete_product/<name>", methods=["POST", "GET"])
def delete_product(name):
    students.delete_one({"Name": name})
    return jsonify({"message": "Product deleted successfully"}), 200

@app.route("/api/add_product", methods=["POST"])
def add_product():
    new_product = {
        "Name":        request.form.get("Product_name"),
        "Description": request.form.get("Description"),
        "Stock":       int(request.form.get("Stock")),
        "Price":       float(request.form.get("Price")),
    }

    if students.find_one({"Name": new_product["Name"]}):
        return jsonify({"error": "Product with this name already exists"}), 400

    students.insert_one(new_product)
    return redirect("/add_product")


# ----------------------------------------------------------------------------------- run the app
if __name__ == "__main__":
    app.run(debug=True)