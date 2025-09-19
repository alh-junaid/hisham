from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret")

# MongoDB connection (service name 'mongo' from docker-compose)
app.config["MONGO_URI"] = "mongodb://mongo:27017/expenses_db"
mongo = PyMongo(app)
@app.route('/')
def index():
    category = request.args.get('category')
    if category:
        expenses = mongo.db.expenses.find({"category": category}).sort("date", -1)
    else:
        expenses = mongo.db.expenses.find().sort("date", -1)
    categories = mongo.db.expenses.distinct("category")
    return render_template("index.html", expenses=expenses, categories=categories)

@app.route('/add', methods=['POST'])
def add_expense():
    try:
        expense = {
            "description": request.form["description"],
            "amount": float(request.form["amount"]),
            "category": request.form["category"],
            "date": datetime.strptime(request.form["date"], "%Y-%m-%d")
        }
        mongo.db.expenses.insert_one(expense)
        flash("Expense added", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    return redirect(url_for("index"))

@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_expense(id):
    expense = mongo.db.expenses.find_one({"_id": ObjectId(id)})
    if request.method == "POST":
        mongo.db.expenses.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "description": request.form["description"],
                "amount": float(request.form["amount"]),
                "category": request.form["category"],
                "date": datetime.strptime(request.form["date"], "%Y-%m-%d")
            }}
        )
        flash("Expense updated", "success")
        return redirect(url_for("index"))
    return render_template("edit.html", expense=expense)

@app.route('/delete/<id>', methods=['POST'])
def delete_expense(id):
    mongo.db.expenses.delete_one({"_id": ObjectId(id)})
    flash("Expense deleted", "success")
    return redirect(url_for("index"))

# API endpoints
@app.route('/api/expenses', methods=['GET'])
def api_get_expenses():
    expenses = list(mongo.db.expenses.find().sort("date", -1))
    for e in expenses:
        e["_id"] = str(e["_id"])
        e["date"] = e["date"].strftime("%Y-%m-%d")
    return jsonify(expenses)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
