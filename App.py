#Importing Flask framework and rendering templates
from flask import Flask, render_template, request, redirect, url_for, session
#Importing variables from config files
from Config import connection,cur
import sqlite3
app=Flask(__name__)
#needed for session
app.secret_key = "dev-secret-key"

#Directing up the default/start page
@app.route('/', methods=["GET","POST"])
def login():
    #Really important error is defined or else it brings back an internal error
    error=None

    if request.method=="POST":
        Username=request.form["Username"]
        Password=request.form["Password"]
#Pulling up records from the database where the inputted form username and password matches. The user must also be active 
        cur.execute("SELECT * FROM users WHERE Email_Address=? AND Passwords=? AND Is_Active=1",(Username, Password))

        Loginreq=cur.fetchone()
#If there is a match go the the dashboard html, if not display an error on screen
        if Loginreq:
             #checks and saves the system role
             session["Sys_Role"]=Loginreq[4]
             
             return redirect(url_for('Dashboard'))
        else:
            error="Invalid, please check your username and password"
    
    return render_template ("login.html",error=error)



#Directing the Asset Assignment page
@app.route('/Asset_Assignment', methods=["Get","Post"])
def Asset_Assignment():
    #Assigment list - Asset assignment table, asset table and users
    cur.execute("""
        SELECT aa.AssignmentID, a.Asset_Description, u.Full_Name, a.Serial_Number, aa.Assigned_Date, a.Asset_Status 
        FROM asset_assignment aa
        JOIN assets a ON aa.AssetID = a.AssetID
        JOIN users u ON aa.UserID = u.UserID
    """)
    assignment_list = cur.fetchall()

#Setting up admin section for assignment
    users = []
    available_assets = []
    
    cur.execute("SELECT UserID, Full_Name FROM users WHERE Is_Active=1")
    users = cur.fetchall()
    cur.execute("SELECT AssetID, Asset_Description FROM assets WHERE Asset_Status='Available'")
    available_assets = cur.fetchall()


    return render_template("Asset Assignment.html", asset_assignment_list=assignment_list, users=users, assets=available_assets)

@app.route('/assign_asset', methods=['POST'])
def assign_asset():
    user_id = request.form.get('user_id')
    asset_id = request.form.get('asset_id')
        
        # Insert into assignment table
    cur.execute("""
        INSERT INTO asset_assignment (AssignmentID, UserID, AssetID, Assigned_Date) 
        VALUES (?, ?, ?, CURRENT_DATE)
        """, (f"ASGN-{asset_id}", user_id, asset_id))
        
        # Update asset status to 'Assigned'
    cur.execute("UPDATE assets SET Asset_Status='Assigned' WHERE AssetID=?", (asset_id,))
    connection.commit()
        
    return redirect(url_for('Asset_Assignment'))

#### ASSET SEECTION

#Directing the Assets page
@app.route('/Assets')
def Assets():
    cur.execute("SELECT AssetID, Asset_Description, Asset_Type, Serial_Number, Purchased_Date, Asset_Status FROM Assets")
    assetlist=cur.fetchall()
    return render_template ("Assets.html", asset_list=assetlist, edit_asset=None)

#Edit assets
@app.route('/edit_asset/<asset_id>')
def edit_asset(asset_id):
    cur.execute("SELECT AssetID, Asset_Description, Asset_Type, Serial_Number, Purchased_Date, Asset_Status FROM Assets WHERE AssetID=?", (asset_id,))
    selected_asset = cur.fetchone()

    
    return render_template("Assets.html", edit_asset=selected_asset)


@app.route('/delete_asset/<asset_id>', methods=["POST"])
def delete_asset(asset_id):
    cur.execute("DELETE FROM Assets WHERE AssetID = ?", (asset_id,))
    connection.commit()

    return redirect(url_for('Assets'))

@app.route('/save_asset', methods=['POST'])
#Pulling data from the asset form
def save_asset():
    assetid = request.form.get('asset_id')
    Asset_description = request.form['Asset_Description']
    Asset_Type = request.form['Asset_Type']
    Serial_Number = request.form['Serial_Number']
    Purchase_Date = request.form['Purchase_Date']
    Asset_Status = request.form['Asset_Status']

    
   
    
    # Check if this asset is already exists in the DB
    cur.execute("SELECT AssetID FROM Assets WHERE AssetID = ?", (assetid,))
    exists = cur.fetchone()

    if exists:
        # UPDATE existing record
        cur.execute("""
            UPDATE Assets 
            SET Asset_Description = ?, Asset_Type = ?, Serial_Number = ?, Purchased_Date = ?, Asset_Status = ?
            WHERE AssetID = ?
        """, (Asset_description, Asset_Type , Serial_Number, Purchase_Date , Asset_Status, assetid))
    else:
        # INSERT new record 
        cur.execute("""
        INSERT INTO Assets (AssetID , Asset_Description , Asset_Type, Serial_Number, Purchased_Date, Asset_Status )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (assetid , Asset_description , Asset_Type, Serial_Number, Purchase_Date, Asset_Status))
    connection.commit()
    return redirect(url_for('Assets'))


#DASHBOARD
#Directing the Dashboard page
@app.route('/Dashboard')
def Dashboard():
    return render_template ("Dashboard.html")
    



#USERS SECTION


#Directing the Users page
@app.route('/Users')
def Users():
    cur.execute("SELECT UserID, Full_Name, Email_Address, Sys_Role, Created_At, Is_Active FROM Users")
    userlist=cur.fetchall()
    return render_template ("Users.html", user_list=userlist, edit_user=None)


#to edit user, the path must show the user id so its not just a static path
@app.route('/edit_user/<user_id>')
def edit_user(user_id):
    cur.execute("SELECT UserID, Full_Name, Email_Address, Sys_Role, Created_At, Is_Active, Passwords FROM Users WHERE UserID=?", (user_id,))
    selected_user = cur.fetchone()



    return render_template("Users.html", edit_user=selected_user)

#Delete user
@app.route('/delete_user/<user_id>', methods=["POST"])
def delete_user(user_id):
    cur.execute("DELETE FROM Users WHERE UserID = ?", (user_id,))
    connection.commit()

    return redirect(url_for('Users'))


@app.route('/save_user', methods=['POST'])
#Pulling data from the users form
def save_user():
    userid = request.form.get('user_id')
    full_name = request.form['full_name']
    email = request.form['email']
    sys_role = request.form['sys_role']
    password = request.form['password']
    is_active = 1 if request.form.get('is_active') else 0

    
   
    
    # Check if this user already exists in the DB
    cur.execute("SELECT UserID FROM Users WHERE UserID = ?", (userid,))
    exists = cur.fetchone()

    if exists:
        # UPDATE existing record
        cur.execute("""
            UPDATE Users 
            SET Full_Name = ?, Email_Address = ?, Sys_Role = ?, Is_Active = ?, Passwords = ?
            WHERE UserID = ?
        """, (full_name, email, sys_role, is_active, password, userid))
    else:
        # INSERT new record (time stamp is needed or an error is returned)
        cur.execute("""
        INSERT INTO Users (UserID, Full_Name, Email_Address, Sys_Role, Is_Active, Passwords, Created_At)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (userid, full_name, email, sys_role, is_active, password))
    connection.commit()
    return redirect(url_for('Users'))

# END of Users Section








if __name__ == '__main__': 
 #app.run(debug=True) -- debugging app, troubleshoots errors
 app.run()