import json

from flask import Flask, request, render_template, url_for
from parser import get_full_info

app = Flask(__name__)

with open("sbc.json", "r", encoding="utf-8") as f:
        sbc_list = json.load(f)
        
def compare_products_dynamic(first, second):
    values_product1 = [int(x) for x in first["benchmark"].values() if x.isdigit()]
    values_product2 = [int(x) for x in second["benchmark"].values() if x.isdigit()]

    if len(values_product1) != len(values_product2):
        return "Erorr - the number of values for each product must be the same."
    
    max_values = [max(v1, v2) for v1, v2 in zip(values_product1, values_product2)]

    percentages_product1 = [(v1 / max_v) * 100 for v1, max_v in zip(values_product1, max_values)]
    percentages_product2 = [(v2 / max_v) * 100 for v2, max_v in zip(values_product2, max_values)]

    avg_percentage_product1 = sum(percentages_product1) / len(percentages_product1)
    avg_percentage_product2 = sum(percentages_product2) / len(percentages_product2)

    if avg_percentage_product1 > avg_percentage_product2:
        better_product = first["name"]
        percent_difference = avg_percentage_product1 - avg_percentage_product2
        
    elif avg_percentage_product2 > avg_percentage_product1:
        better_product = second["name"]
        percent_difference = avg_percentage_product2 - avg_percentage_product1
        
    else:
        return "Both products are equally good."

    return (better_product, round(percent_difference, 2))

@app.route('/', methods=['GET', 'POST'])
def index():
    global sbc_list
    if request.method == 'POST':
        first_sbc = request.form.get('first_sbc').strip()
        second_sbc = request.form.get('second_sbc').strip()
        
        isadv_serach = request.form.get('advanced_serach')

        first_sbc = sbc_list.get(first_sbc)
        second_sbc = sbc_list.get(second_sbc)
        
        first = get_full_info(first_sbc, isadv_serach)
        second = get_full_info(second_sbc, isadv_serach)
        
        result = compare_products_dynamic(first, second)

        return render_template('compare.html', first=first, second=second, result=result)
        
    else:
        return render_template('index.html', sbc_list=sbc_list)

if __name__ == "__main__":
    app.run()
    