#CALCULATION ALGORITHMS

def calculate_calories(age, height, weight, activity_level): 
  bmr = 10 * weight + 6.25 * height - 5 * age #CALCULATES BMR
  multipliers = {"BMR": 1.2, "sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725, "very_active": 1.9}

  #MULTIPLIES BMR WITH THE ACTIVITY LEVEL TO CALCULATE CALORIES TO BE CONSUMED /day

  if activity_level in multipliers:
    return bmr * multipliers[activity_level]
  else:
    raise ValueError("Invalid activity level provided.")

def calculate_sleep(sleep_estimation, age):

  #RETURNS THE MINIMUM SLEEP TIME WHICH IS CALCULATED BETWEEN AVERAGE FOR AGE AND SLEEP ESTIMATION
  #MAYBE CHANGE TO sleep_time = (max + sleep_estimation)/2 

  if age < 18:
    return max(8, sleep_estimation)
  elif age < 65:
    return max(7, sleep_estimation)
  else:
    return max(6, sleep_estimation)
  
def calculate_workout(available_time, activity_level):
  multipliers = {"BMR": 0.1, "sedentary": 0.1, "light": 0.2, "moderate": 0.3, "active": 0.5, "very_active": 0.7}

  #CALCULATES THE AVERAGE WEEKLY/DAILY WORKOUT TIME

  if activity_level in multipliers:
    return round(available_time * multipliers[activity_level], 2)
  else:
    raise ValueError("Invalid activity level provided.")