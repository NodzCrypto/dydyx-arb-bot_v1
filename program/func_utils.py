from datetime import datetime, timedelta

# Format number
def format_number(current_num, example_num):

    #give current number an example of number with decimals desired
    #function will return the correctly formatted string

    current_num_string = f"{current_num}"
    example_num_string = f"{example_num}"

    if "." in example_num_string:
        example_decimals = len(example_num_string.split(".")[1])
        current_num_string = f"{current_num:.{example_decimals}f}"    
        current_num_string = current_num_string[:]
        return current_num_string
    else:
        return f"{int(current_num)}"

# format time
def format_time(timestamp):
    return timestamp.replace(microsecond=0).isoformat()

# get ISO Trades
def get_ISO_times():
    date_start_0 = datetime.now()
    date_start_1 = date_start_0 - timedelta(hours=100)
    date_start_2 = date_start_1 - timedelta(hours=100)
    date_start_3 = date_start_2 - timedelta(hours=100)
    date_start_4 = date_start_3 - timedelta(hours=100)

    ##format datetimes
    time_dict = {
        "range1": {
            "from_iso": format_time(date_start_1),
            "to_iso": format_time(date_start_0) 
        },
        "range2": {
            "from_iso": format_time(date_start_2),
            "to_iso": format_time(date_start_1) 
        },
        "range3": {
            "from_iso": format_time(date_start_3),
            "to_iso": format_time(date_start_2) 
        },
        "range4": {
            "from_iso": format_time(date_start_4),
            "to_iso": format_time(date_start_3) 
        }
    }

    #return result
    return time_dict