import streamlit
import pandas
import requests
import snowflake.connector
from urllib.error import URLError 

streamlit.title('Healthy Dinner')
streamlit.header('Breakfast Menu')
streamlit.text('🥣 Omega 3 & Blueberry Oatmeal')
streamlit.text('🥗 Kale, Spinach & Rocket Smoothie')
streamlit.text('🐔 Hard-Boiled Free-Range Egg')
streamlit.text('🥑🍞 Avocado Toast')

# BYOS
streamlit.header('🍌🥭 Build Your Own Fruit Smoothie 🥝🍇')
# read S3 bucket file
my_fruit_list = pandas.read_csv("https://uni-lab-files.s3.us-west-2.amazonaws.com/dabw/fruit_macros.txt")
my_fruit_list = my_fruit_list.set_index('Fruit')
# user pick from list
fruits_selected = streamlit.multiselect("Pick some fruits:", list(my_fruit_list.index))
fruits_to_show = my_fruit_list.loc[fruits_selected]
# add table from S3 bucket file
streamlit.dataframe(fruits_to_show)


# fruityvice api: allow user to query & get response
streamlit.header("Fruityvice Fruit Advice!")
def get_fruityvice_data(this_fruit_choice):
  fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + this_fruit_choice)
  # pretify json reponse 
  fruityvice_normalized = pandas.json_normalize(fruityvice_response.json())
  # create table from response
  return fruityvice_normalized

# take user input
try:
  fruit_choice = streamlit.text_input('What fruit would you like information about?')
  if not fruit_choice:
    streamlit.error("Enter a fruit to get information")
  else:
    back_from_function = get_fruityvice_data(fruit_choice)
    streamlit.dataframe(back_from_function)
except URLError as e:
  streamlit.error()

  
# snowflake connect: allow user to read and write data from sf
streamlit.header("View Our Fruit List & Add Your Favorites!")
def get_fruit_load_list():
  with  my_cnx.cursor() as my_cur:
    # query data 
    my_cur.execute("select * from pc_rivery_db.public.fruit_load_list")
    return my_cur.fetchall()
  
# button to load data
if streamlit.button('Get Fruit List'):
  # read data
  my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
  my_data_rows = get_fruit_load_list()
  my_cnx.close()
  streamlit.dataframe(my_data_rows)
  
# allow user add fruit to the list
def insert_row_snowflake(new_fruit):
  with my_cnx.cursor() as my_cur:
    # write data
    my_cur.execute("insert into pc_rivery_db.public.fruit_load_list values ('" + new_fruit + "')")
    my_cnx.close()
    return ('Thanks for adding ', new_fruit)
# take user input
add_my_fruit = streamlit.text_input('What fruit would you like to add')
if streamlit.button('Add a fruit to the list'):
    # connect SF metadata
    my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
    back_from_function = insert_row_snowflake(add_my_fruit)
    streamlit.text(back_from_function)

# stop
#streamlit.stop()
