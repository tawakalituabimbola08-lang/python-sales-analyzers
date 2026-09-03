sales = [12000, 8500, 15000, 7000, 22000]

total = sum(sales)
average = total / len(sales)
highest = max(sales)
lowest = min(sales)
number_of_sales = len(sales)

print("===== SALES REPORT =====")
print("Total sales:", total)
print("Average sale:", average)
print("Highest sale:", highest)
print("Lowest sale:", lowest)
print("Number of sales:", number_of_sales)