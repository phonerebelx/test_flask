from flask import Flask,jsonify,request, render_template
from flask_cors import CORS
import xmlrpc.client
import sys
app = Flask(__name__)
CORS(app)
@app.route("/odoo_authentication",methods=["POST"])
def odoo_authentication():
    response_obj = {
        "status" : "fail",
        "message" : "something went wrong"
    }
    try:
        post_data=request.get_json()
        
        url = post_data.get("url")
        db = post_data.get("db")
        username = post_data.get("username")
        password = post_data.get("password")
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db,username,password,{})
        
        if uid:
            response_obj["token"] = uid
            response_obj["status"] = "success"
            response_obj["message"] = "authenticated"
        else:
            response_obj["message"] = "authentication error"
        
    
   
        return jsonify(response_obj)
    except Exception as e:
        response_obj["error"] = str(e)
        
        return jsonify(response_obj)

@app.route("/create_invoice",methods=["POST"])
def create_invoice():
    response_obj = {
        "status" : "fail",
        "message" : "something went wrong"
    }
    try:
        post_data=request.get_json()
        url = post_data.get("url")
        db = post_data.get("db")
        uid = post_data.get("token")  
        password = post_data.get("password")    
        partner_id =  post_data.get("partner_id")
        partner_name = post_data.get("partner_name")
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        if partner_id == 0:
            partner_id = models.execute_kw(db, uid, password, 'res.partner', 'create', [{'name': partner_name}])
        items_array = post_data.get("items_array")
        items = []
        for i in items_array:
            if i["product_id"] == 0:
                i["product_id"] = models.execute_kw(db, uid, password,'product.product', 'create', [{'name': i["product_name"],'list_price': i["price_unit"]}])
                del i["product_name"]
            items.append((0,0,i))
        invoice_id = models.execute_kw(db, uid,password, 'account.move', 'create', [{"partner_id":partner_id,'ref':"None",'move_type':'out_invoice',"invoice_line_ids":items}])
        models.execute_kw(db, uid, password, 'account.move', 'action_post', [[invoice_id]])
        invoice = models.execute_kw(db, uid, password, 'account.move', 'search_read', [[['id', '=', invoice_id]]])
        response_obj["invoice_obj"] = invoice
        response_obj["status"] = "success"
        response_obj["message"] = "Invoice created successfully"
        return jsonify(response_obj)

    
    except Exception as e:
        response_obj["error"] = str(e)
        
        return jsonify(response_obj)

if __name__ == "__main__":
    app.run(debug=False,host="0.0.0.0")