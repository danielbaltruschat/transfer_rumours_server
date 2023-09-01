try:
    with open("prev_time.txt", "r") as f:
        prev_time = int(f.read())
except:
    prev_time = 0
    with open("prev_time.txt", "w") as f:
        f.write(str(prev_time))
        
print(prev_time)