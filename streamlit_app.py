import streamlit
import pandas
import requests
import snowflake.connector
from urllib.error import URLError 

streamlit.title('Healthy Dinner')
streamlit.header('Breakfast Menu')
streamlit.text('🥣 Omega 3 & Blueberry Oatmeal')
streamlit.text(' 🥗 Kale, Spinach & Rocket Smoothie')
streamlit.text('🐔 Hard-Boiled Free-Range Egg')
streamlit.text('🥑🍞 Avocado Toast')

# pandas
streamlit.header('🍌🥭 Build Your Own Fruit Smoothie 🥝🍇')
# read S3 bucket file
my_fruit_list = pandas.read_csv("https://uni-lab-files.s3.us-west-2.amazonaws.com/dabw/fruit_macros.txt")
my_fruit_list = my_fruit_list.set_index('Fruit')

# pick list
# fruits_selected = streamlit.multiselect("Pick some fruits:", list(my_fruit_list.index),['Avocado', 'Strawberries'])
fruits_selected = streamlit.multiselect("Pick some fruits:", list(my_fruit_list.index))
fruits_to_show = my_fruit_list.loc[fruits_selected]
# add table from S3 bucket file
streamlit.dataframe(fruits_to_show)

# requests
# fruityvice api response
def get_fruityvice_data(this_fruit_choice):
  fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + this_fruit_choice)
    # pretify json reponse 
    fruityvice_normalized = pandas.json_normalize(fruityvice_response.json())
    # create table from response
    return fruityvice_normalized
  
streamlit.header("Fruityvice Fruit Advice!")
# allow user input
try:
  fruit_choice = streamlit.text_input('What fruit would you like information about?')
  if not fruit_choice:
    streamlit.error("Enter a fruit to get information")
  else:
    back_from_function = get_fruityvice_data(fruit_choice)
    streamlit.dataframe(back_from_function)
except URLError as e:
  streamlit.error()
  
# stop
streamlit.stop()

# snowflake connector
# connect SF metadata
my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
my_cur = my_cnx.cursor()
# query data
my_cur.execute("select * from pc_rivery_db.public.fruit_load_list")
my_data_rows = my_cur.fetchall()
streamlit.header("Fruit List:")
streamlit.dataframe(my_data_rows)
# allow user input
add_my_fruit = streamlit.text_input('What fruit would you like to add')
streamlit.write('Thanks for adding ', add_my_fruit)
my_cur.execute("insert into pc_rivery_db.public.fruit_load_list values ('from streamlit')")
