import streamlit as st
import easyocr
import mysql.connector
import cv2
import numpy as np 
import pandas as pd
from mysql.connector import Error

# Connect to MySQL database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Jaga7375@",
    database="bizcard")

# Create a cursor object to execute SQL queries
mycursor = mydb.cursor()

# Create a table to store the business card information
mycursor.execute("CREATE TABLE IF NOT EXISTS card (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), job_title VARCHAR(255), address VARCHAR(255), postcode VARCHAR(255), phone VARCHAR(255), email VARCHAR(255), website VARCHAR(255), company_name VARCHAR(225))")

# Create an OCR object to read text from the image
reader = easyocr.Reader(['en'])

st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://cdn.wallpapersafari.com/53/63/pnd4MG.jpg");
             background-attachment: fixed;
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True

        )

#display 
st.title(":[Extracting Business Card Data with OCR]")

# Create a file uploader widget
uploaded_file = st.file_uploader("Upload a business card image", type=["jpg", "jpeg", "png"])

# Create a sidebar menu with options to add, view, update, and delete business card information
menu = ['Add', 'View', 'Update', 'Delete']
select = st.sidebar.selectbox("Select an option", menu)

if select == 'Add':
    if uploaded_file is not None:
        # Read the image using OpenCV

        image = cv2.imdecode(np.fromstring(uploaded_file.read(), np.uint8), 1)
        # Display the uploaded image

        st.image(image, caption='Uploaded business card image', use_column_width=True)
        # Create a button to extract information from the image

        if st.button('Data Extract Information'):
            # Call the function to data extract the information from the image
            bounds = reader.readtext(image, detail=0)

            text = "\n".join(bounds)

            # Insert the data extracted information and image into the database
            sql = "INSERT INTO card(name, job_title, address, postcode, phone, email, website, company_name) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (bounds[0], bounds[1], bounds[2], bounds[3], bounds[4], bounds[5], bounds[6], bounds[7])
            mycursor.execute(sql, val)
            mydb.commit()
            # Display a success message
            st.success("Business card information added to database.")

elif select == 'View':
    # Display the stored business card information
    mycursor.execute("SELECT * FROM card")
    result = mycursor.fetchall()
    df = pd.DataFrame(result, columns=['id','name', 'job_title', 'address', 'postcode', 'phone', 'email', 'website', 'company_name'])
    st.write(df)

elif select == 'Update':
    # Create a dropdown menu to select a business card to update
    mycursor.execute("SELECT id, name FROM card")
    result = mycursor.fetchall()
    business_cards = {}
    for row in result:
        business_cards[row[1]] = row[0]
    selected_card_name = st.selectbox("Select a business card to update", list(business_cards.keys()))

    # Get the current information for the selected business card
    mycursor.execute("SELECT * FROM card WHERE name=%s", (selected_card_name,))
    result = mycursor.fetchone()

    # Display the current information for the selected business card
    st.write("Name:", result[1])
    st.write("Job Title:", result[2])
    st.write("Address:", result[3])
    st.write("Postcode:", result[4])
    st.write("Phone:", result[5])
    st.write("Email:", result[6])
    st.write("Website:", result[7])
    st.write("company_name:", result[8])

    # Get new information for the business card
    name = st.text_input("Name", result[1])
    job_title = st.text_input("Job Title", result[2])
    address = st.text_input("Address", result[3])
    postcode = st.text_input("Postcode", result[4])
    phone = st.text_input("Phone", result[5])
    email = st.text_input("Email", result[6])
    website = st.text_input("Website", result[7])
    company_name = st.text_input("Company Name", result[8])

    # Create a button to update the business card
    if st.button("Update Business Card"):
        # Update the information for the selected business card in the database
        mycursor.execute("UPDATE card SET name=%s, job_title=%s, address=%s, postcode=%s, phone=%s, email=%s, website=%s, company_name=%s WHERE name=%s", 
                             (name, job_title, address, postcode, phone, email, website, company_name, selected_card_name))
        mydb.commit()
        st.success("Business card information updated in database.")

elif select == 'Delete':
    # Create a dropdown menu to select a business card to delete
    mycursor.execute("SELECT id, name FROM card")
    result = mycursor.fetchall()
    business_cards = {}
    for row in result:
        business_cards[row[0]] = row[1]
    selected_card_id = st.selectbox("Select a business card to delete", list(business_cards.keys()), format_func=lambda x: business_cards[x])

    # Get the name of the selected business card
    mycursor.execute("SELECT name FROM card WHERE id=%s", (selected_card_id,))
    result = mycursor.fetchone()
    selected_card_name = result[0]

    # Display the current information for the selected business card
    st.write("Name:", selected_card_name)
    # Display the rest of the information for the selected business card

    # Create a button to confirm the deletion of the selected business card
    if st.button("Delete Business Card"):
        mycursor.execute("DELETE FROM card WHERE name=%s", (selected_card_name,))
        mydb.commit()
        st.success("Business card information deleted from database.")