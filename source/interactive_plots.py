import pandas as pd
from ipywidgets import widgets
import plotly.graph_objects as go
from datetime import datetime

def interactive_histogram(button_info, data, x_axis_label, y_axis_label): 

    # initialize dictionary to store buttons
    button_dict = {"categories": [], 
                "data": None 
                }

    # create buttons filter on categories and store in dict         
    for button in button_info["categories"]: 
        widget = widgets.Dropdown(
            description=button["name"],
            options=["All"] + data[button["column"]].unique().tolist()
        )
        button_dict["categories"].append(widget)

    # create button to filter data columns and store in dict
    widget = widgets.Dropdown(
        options=button_info["data"]["columns"],
        description=button_info["data"]["name"]
    )
    button_dict["data"] = widget

    # create figure
    g = go.FigureWidget()

    # create histogram traces for each data column
    for col in button_info["data"]["columns"]: 
        g.add_trace(
            go.Histogram(x=data[col], opacity=0.75, name=col, marker_color="#7C002E") 
        )

    def validate(): # function to ensure that value delivered by button is in dataframe    
        validation_bool = []

        # cycle through each category filter button
        for info, button in zip(button_info["categories"], button_dict["categories"]): 
            # ensure that button option is in dataframe or "All" (i.e., don't filter) is selected
            if button.value in data[info["column"]].unique() or button.value == "All": 
                validation_bool.append(True) 
            else: 
                validation_bool.append(False) 

        # ensure that data column filter button option is in dataframe or "All" (i.e., don't filter) is selected
        if button_dict["data"].value in button_info["data"]["columns"]: 
                validation_bool.append(True)
        else: 
                validation_bool.append(False)

        # ensure that value condition is met for all buttons
        if False not in validation_bool:    
            return True
        else:
            return False

    def response(change): # function to dictate data filtering update upon change
        if validate(): # if all button values are in dataframe

            # get button names
            button_names = [button.description for button in button_dict["categories"]]
            # create dictionary to store list of booleans for filtering
            filters = dict.fromkeys(button_names)

            # cycle through filter category buttons and list of booleans to dict
            for info, button in zip(button_info["categories"], button_dict["categories"]): 
                
                if button.value == "All": # don't filter
                    filters[button.description] = pd.Series([True] * data.shape[0])
                else: # filter based on button value
                    filters[button.description] = data[info["column"]] == button.value

            # get list of boolean values for each row filtering on category buttons; apply to dataframe
            filters_df = pd.DataFrame({key: filters[key].to_list() for key in filters.keys()})
            filter_list = filters_df.all(axis='columns').to_list()
            temp_df = data[filter_list]
            
            # apply filter to each data column
            x =  [None] * len(g.data)
            for i, col in enumerate(button_info["data"]["columns"]):
                x[i] = temp_df[col]

            # set visibility for each column/trace based on data filter button
            visibilities = [False] * len(g.data) # initialize visibilities for traces (data columns)
            visible_index = button_info["data"]["columns"].index(button_dict["data"].value) # get index for data button value
            visibilities[visible_index] = True # set the visibility of that column/trace to visible

            # set data for histogram based on filtering from category buttons and data button
            with g.batch_update(): # required to update data
                for i, visibility in enumerate(visibilities): 
                    g.data[i].x = x[i]
                    g.data[i].visible = visibility

    # label histogram
    g.layout.xaxis.title = x_axis_label
    g.layout.yaxis.title = y_axis_label

    # set each button to update according to button filtering
    for button in button_dict["categories"] + [button_dict["data"]]:
        button.observe(response, names="value")

    # initialize dictionary for button containers (for button placement)
    button_containers = {"1": [button_dict["data"]], "2": []}

    # add buttons to respective containers
    for info, button in zip(button_info["categories"], button_dict["categories"]): 
        button_containers[str(info["button row"])].append(button)

    # display histogram   
    return widgets.VBox([widgets.HBox(button_containers["1"]), 
                        widgets.HBox(button_containers["2"]), 
                        g])

def interactive_violin(button_info, data, y_axis_label): 

    # initialize dictionary to store buttons
    button_dict = {"categories": [], 
                "data": None 
                }

    # create buttons filter on categories and store in dict         
    for button in button_info["categories"]: 
        widget = widgets.Dropdown(
            description=button["name"],
            options=["All"] + data[button["column"]].unique().tolist()
        )
        button_dict["categories"].append(widget)

    # create button to filter data columns and store in dict
    widget = widgets.Dropdown(
        options=button_info["data"]["columns"],
        description=button_info["data"]["name"]
    )
    button_dict["data"] = widget

    # create figure
    g = go.FigureWidget()

    # create violin plot traces for each data column
    for col in button_info["data"]["columns"]: 
        g.add_trace(
            go.Violin(y=data[col], opacity=0.6, name="", box_visible=True, \
                    line_color="black", fillcolor='lightseagreen', \
                    meanline_visible=True, points="all") 
        )

    def validate(): # function to ensure that value delivered by button is in dataframe    
        validation_bool = []

        # cycle through each category filter button
        for info, button in zip(button_info["categories"], button_dict["categories"]): 
            # ensure that button option is in dataframe or "All" (i.e., don't filter) is selected
            if button.value in data[info["column"]].unique() or button.value == "All": 
                validation_bool.append(True) 
            else: 
                validation_bool.append(False) 

        # ensure that data column filter button option is in dataframe
        if button_dict["data"].value in button_info["data"]["columns"]: 
                validation_bool.append(True)
        else: 
                validation_bool.append(False)

        # ensure that value condition is met for all buttons
        if False not in validation_bool:    
            return True
        else:
            return False

    def response(change): # function to dictate data filtering update upon change
        if validate(): # if all button values are in dataframe

            # get button names
            button_names = [button.description for button in button_dict["categories"]]
            # create dictionary to store list of booleans for filtering
            filters = dict.fromkeys(button_names)

            # cycle through filter category buttons and list of booleans to dict
            for info, button in zip(button_info["categories"], button_dict["categories"]): 
                
                if button.value == "All": # don't filter
                    filters[button.description] = pd.Series([True] * data.shape[0])
                else: # filter based on button value
                    filters[button.description] = data[info["column"]] == button.value

            # get list of boolean values for each row filtering on category buttons; apply to dataframe
            filters_df = pd.DataFrame({key: filters[key].to_list() for key in filters.keys()})
            filter_list = filters_df.all(axis='columns').to_list()
            temp_df = data[filter_list]
            
            # apply filter to each data column
            x =  [None] * len(g.data)
            for i, col in enumerate(button_info["data"]["columns"]):
                x[i] = temp_df[col]

            # set visibility for each column/trace based on data filter button
            visibilities = [False] * len(g.data) # initialize visibilities for traces (data columns)
            visible_index = button_info["data"]["columns"].index(button_dict["data"].value) # get index for data button value
            visibilities[visible_index] = True # set the visibility of that column/trace to visible

            # set data for violin plot based on filtering from category buttons and data button
            with g.batch_update(): # required to update data
                for i, visibility in enumerate(visibilities): 
                    g.data[i].y = x[i]
                    g.data[i].visible = visibility

    # label violin plot
    g.layout.yaxis.title = y_axis_label

    # set each button to update according to button filtering
    for button in button_dict["categories"] + [button_dict["data"]]:
        button.observe(response, names="value")

    # initialize dictionary for button containers (for button placement)
    button_containers = {"1": [button_dict["data"]], "2": []}

    # add buttons to respective containers
    for info, button in zip(button_info["categories"], button_dict["categories"]): 
        button_containers[str(info["button row"])].append(button)

    # display violin plot   
    return widgets.VBox([widgets.HBox(button_containers["1"]), 
                        widgets.HBox(button_containers["2"]), 
                        g])

def interactive_linear_regression_plot(button_info, model_results, x_axis_label, y_axis_label, title): 

    # initialize dictionary to store buttons
    button_dict = {"data": None }

    # create button to filter data columns and store in dict
    widget = widgets.Dropdown(
        options=button_info["data"]["columns"],
        description=button_info["data"]["name"]
    )
    button_dict["data"] = widget

    # create figure
    g = go.FigureWidget(layout_title_text=title)

    # create histogram traces for each data column
    for col in button_info["data"]["columns"]: 
        r_squared = round(model_results[col]["score"], 3)
        g.add_trace(
            go.Scatter(x=[datetime.fromordinal(date) for date in model_results[col]["x_train"].squeeze()],
                       y=model_results[col]["y_train"].squeeze(), 
                       name="data",
                       mode="markers"
            )       
        )        
        g.add_trace(
            go.Scatter(x=[datetime.fromordinal(date) for date in model_results[col]["x_predict"].squeeze()], 
                       y=model_results[col]["y_predict"].squeeze(), 
                       name=f"line of best fit (R squared = {r_squared})",
                       mode="lines"
            )       
        )


    def validate(): # function to ensure that value delivered by button is in dataframe    
        validation_bool = []

        # ensure that data column filter button option is in dataframe
        if button_dict["data"].value in model_results.keys(): 
                validation_bool.append(True)
        else: 
                validation_bool.append(False)

        # ensure that value condition is met for all buttons
        if False not in validation_bool:    
            return True
        else:
            return False

    def response(change): # function to dictate data filtering update upon change
        if validate(): # if all button values are in dataframe

            # set visibility for each column/trace based on data filter button
            visibilities = [False] * len(g.data) # initialize visibilities for traces (data columns)
            visible_index = button_info["data"]["columns"].index(button_dict["data"].value) * 2 # get index for data button value
            visibilities[visible_index] = True # set the visibility of that column/trace to visible
            visibilities[visible_index+1] = True

            # set data for histogram based on filtering from category buttons and data button
            with g.batch_update(): # required to update data
                for i, visibility in enumerate(visibilities): 
                    g.data[i].visible = visibility

    # label histogram
    g.layout.xaxis.title = x_axis_label
    g.layout.yaxis.title = y_axis_label

    g.layout.xaxis.tickvals = [datetime.fromordinal(date) for date in model_results[col]["x_predict"].squeeze()]

    # set each button to update according to button filtering
    button_dict["data"].observe(response, names="value")

    # display histogram   
    return widgets.VBox([widgets.HBox([button_dict["data"]]), g])

def interactive_linear_regression_calibration_plot(button_info, model_results, x_axis_label, y_axis_label, title): 

    # initialize dictionary to store buttons
    button_dict = {"data": None }

    # create button to filter data columns and store in dict
    widget = widgets.Dropdown(
        options=button_info["data"]["columns"],
        description=button_info["data"]["name"]
    )
    button_dict["data"] = widget

    # create figure
    g = go.FigureWidget(layout_title_text=title)

    # create histogram traces for each data column
    for col in button_info["data"]["columns"]: 
        r_squared = round(model_results[col]["score"], 3)
        g.add_trace(
            go.Scatter(x=model_results[col]["x_train"],
                       y=model_results[col]["y_train"], 
                       name="data",
                       mode="markers"
            )       
        )        
        g.add_trace(
            go.Scatter(x=model_results[col]["y_predict"], 
                       y=model_results[col]["x_predict"], 
                       name=f"line of best fit (R squared = {r_squared})",
                       mode="lines"
            )       
        )


    def validate(): # function to ensure that value delivered by button is in dataframe    
        validation_bool = []

        # ensure that data column filter button option is in dataframe
        if button_dict["data"].value in model_results.keys(): 
                validation_bool.append(True)
        else: 
                validation_bool.append(False)

        # ensure that value condition is met for all buttons
        if False not in validation_bool:    
            return True
        else:
            return False

    def response(change): # function to dictate data filtering update upon change
        if validate(): # if all button values are in dataframe

            # set visibility for each column/trace based on data filter button
            visibilities = [False] * len(g.data) # initialize visibilities for traces (data columns)
            visible_index = button_info["data"]["columns"].index(button_dict["data"].value) * 2 # get index for data button value
            visibilities[visible_index] = True # set the visibility of that column/trace to visible
            visibilities[visible_index+1] = True

            # set data for histogram based on filtering from category buttons and data button
            with g.batch_update(): # required to update data
                for i, visibility in enumerate(visibilities): 
                    g.data[i].visible = visibility

    # label histogram
    g.layout.xaxis.title = x_axis_label
    g.layout.yaxis.title = y_axis_label

    # set each button to update according to button filtering
    button_dict["data"].observe(response, names="value")

    # display histogram   
    return widgets.VBox([widgets.HBox([button_dict["data"]]), g])