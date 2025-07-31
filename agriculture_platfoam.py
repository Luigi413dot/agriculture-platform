import json
import os
from datetime import datetime, timedelta

# Data storage files
FARMERS_FILE = "farmers.json"
PRODUCTS_FILE = "products.json"
BIDS_FILE = "bids.json"

# Initialize data files if they don't exist
def initialize_files():
    for file in [FARMERS_FILE, PRODUCTS_FILE, BIDS_FILE]:
        if not os.path.exists(file):
            with open(file, 'w') as f:
                json.dump([], f)

# Load data from JSON files
def load_data(filename):
    with open(filename, 'r') as f:
        return json.load(f)

# Save data to JSON files
def save_data(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# Farmer registration
def register_farmer():
    print("\n=== Farmer Registration ===")
    farmers = load_data(FARMERS_FILE)
    
    username = input("Enter a username: ")
    # Check if username exists
    if any(farmer['username'] == username for farmer in farmers):
        print("Username already exists. Please choose another.")
        return
    
    password = input("Enter a password: ")
    name = input("Enter your full name: ")
    location = input("Enter your location (district): ")
    phone = input("Enter your phone number: ")
    
    new_farmer = {
        'username': username,
        'password': password,  # Note: In real app, hash the password
        'name': name,
        'location': location,
        'phone': phone,
        'verified': False,
        'certificates': []
    }
    
    farmers.append(new_farmer)
    save_data(farmers, FARMERS_FILE)
    print("Registration successful! Please login.")

# Farmer login
def farmer_login():
    print("\n=== Farmer Login ===")
    farmers = load_data(FARMERS_FILE)
    
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    
    for farmer in farmers:
        if farmer['username'] == username and farmer['password'] == password:
            print(f"Welcome back, {farmer['name']}!")
            return farmer
    
    print("Invalid username or password.")
    return None

# Add a new product
def add_product(farmer):
    print("\n=== Add New Product ===")
    products = load_data(PRODUCTS_FILE)
    
    product_name = input("Enter product name: ")
    description = input("Enter product description: ")
    quantity = input("Enter quantity (e.g., 10kg, 5 bags): ")
    quality = input("Enter quality (e.g., Grade A, Organic): ")
    
    print("\nChoose selling method:")
    print("1. Fixed Price")
    print("2. Auction")
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == '1':
        price = float(input("Enter fixed price: "))
        auction = False
        end_date = None
    elif choice == '2':
        starting_price = float(input("Enter starting price: "))
        duration = int(input("Enter auction duration in days: "))
        end_date = (datetime.now() + timedelta(days=duration)).isoformat()
        auction = True
        price = starting_price
    else:
        print("Invalid choice. Product not added.")
        return
    
    new_product = {
        'id': len(products) + 1,
        'farmer_username': farmer['username'],
        'name': product_name,
        'description': description,
        'quantity': quantity,
        'quality': quality,
        'price': price,
        'is_auction': auction,
        'end_date': end_date,
        'sold': False,
        'created_at': datetime.now().isoformat()
    }
    
    products.append(new_product)
    save_data(products, PRODUCTS_FILE)
    print("Product added successfully!")

# View all products
def view_products():
    products = load_data(PRODUCTS_FILE)
    print("\n=== Available Products ===")
    
    for idx, product in enumerate(products, 1):
        if not product['sold']:
            print(f"\nProduct {idx}:")
            print(f"Name: {product['name']}")
            print(f"Description: {product['description']}")
            print(f"Quantity: {product['quantity']}")
            print(f"Quality: {product['quality']}")
            print(f"Price: {product['price']}")
            print(f"Seller: {product['farmer_username']}")
            
            if product['is_auction']:
                print("Type: Auction")
                end_date = datetime.fromisoformat(product['end_date'])
                time_left = end_date - datetime.now()
                print(f"Time left: {time_left.days} days, {time_left.seconds//3600} hours")
            else:
                print("Type: Fixed Price")

# Search products
def search_products():
    products = load_data(PRODUCTS_FILE)
    print("\n=== Search Products ===")
    
    search_term = input("Enter product name or description to search: ").lower()
    location_filter = input("Enter location to filter (leave blank for all): ").lower()
    
    farmers = load_data(FARMERS_FILE)
    matched_products = []
    
    for product in products:
        if not product['sold']:
            farmer = next((f for f in farmers if f['username'] == product['farmer_username']), None)
            if farmer:
                matches_search = (search_term in product['name'].lower() or 
                                 search_term in product['description'].lower())
                matches_location = (not location_filter or 
                                   location_filter in farmer['location'].lower())
                
                if matches_search and matches_location:
                    matched_products.append((product, farmer))
    
    if not matched_products:
        print("No products match your search.")
        return
    
    print(f"\nFound {len(matched_products)} matching products:")
    for idx, (product, farmer) in enumerate(matched_products, 1):
        print(f"\nProduct {idx}:")
        print(f"Name: {product['name']}")
        print(f"Description: {product['description']}")
        print(f"Quantity: {product['quantity']}")
        print(f"Price: {product['price']}")
        print(f"Location: {farmer['location']}")
        print(f"Seller: {farmer['name']} ({farmer['username']})")

# Place a bid on an auction product
def place_bid(buyer_username):
    products = load_data(PRODUCTS_FILE)
    bids = load_data(BIDS_FILE)
    
    print("\n=== Available Auction Products ===")
    auction_products = [p for p in products if p['is_auction'] and not p['sold']]
    
    if not auction_products:
        print("No auction products available.")
        return
    
    for idx, product in enumerate(auction_products, 1):
        print(f"\n{idx}. {product['name']} - Current Price: {product['price']}")
    
    try:
        choice = int(input("\nEnter product number to bid on: ")) - 1
        if choice < 0 or choice >= len(auction_products):
            print("Invalid selection.")
            return
        
        selected_product = auction_products[choice]
        current_price = selected_product['price']
        
        bid_amount = float(input(f"Enter your bid (must be higher than {current_price}): "))
        if bid_amount <= current_price:
            print("Bid must be higher than current price.")
            return
        
        # Update product price
        selected_product['price'] = bid_amount
        save_data(products, PRODUCTS_FILE)
        
        # Record the bid
        new_bid = {
            'product_id': selected_product['id'],
            'buyer_username': buyer_username,
            'amount': bid_amount,
            'timestamp': datetime.now().isoformat()
        }
        bids.append(new_bid)
        save_data(bids, BIDS_FILE)
        
        print(f"Bid of {bid_amount} placed successfully on {selected_product['name']}!")
        
    except ValueError:
        print("Invalid input. Please enter a number.")

# Main menu
def main_menu():
    initialize_files()
    current_user = None
    
    while True:
        print("\n=== Agricultural Product Marketing Platform ===")
        print("1. Farmer Registration")
        print("2. Farmer Login")
        print("3. View All Products")
        print("4. Search Products")
        print("5. Place Bid (for Buyers)")
        print("6. Exit")
        
        choice = input("Enter your choice (1-6): ")
        
        if choice == '1':
            register_farmer()
        elif choice == '2':
            current_user = farmer_login()
            if current_user:
                farmer_menu(current_user)
        elif choice == '3':
            view_products()
        elif choice == '4':
            search_products()
        elif choice == '5':
            buyer_username = input("Enter your username (as buyer): ")
            place_bid(buyer_username)
        elif choice == '6':
            print("Thank you for using our platform. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

# Farmer menu
def farmer_menu(farmer):
    while True:
        print("\n=== Farmer Dashboard ===")
        print(f"Welcome, {farmer['name']}!")
        print("1. Add New Product")
        print("2. View My Products")
        print("3. View Notifications")
        print("4. Logout")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == '1':
            add_product(farmer)
        elif choice == '2':
            view_my_products(farmer)
        elif choice == '3':
            view_notifications(farmer)
        elif choice == '4':
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please try again.")

# View farmer's products
def view_my_products(farmer):
    products = load_data(PRODUCTS_FILE)
    my_products = [p for p in products if p['farmer_username'] == farmer['username']]
    
    print("\n=== My Products ===")
    if not my_products:
        print("You haven't listed any products yet.")
        return
    
    for product in my_products:
        status = "Sold" if product['sold'] else "Available"
        print(f"\n{product['name']} - {status}")
        print(f"Price: {product['price']}")
        if product['is_auction']:
            end_date = datetime.fromisoformat(product['end_date'])
            time_left = end_date - datetime.now()
            if time_left.total_seconds() > 0:
                print(f"Auction ends in: {time_left.days} days")
            else:
                print("Auction ended")

# View notifications
def view_notifications(farmer):
    products = load_data(PRODUCTS_FILE)
    bids = load_data(BIDS_FILE)
    
    print("\n=== Notifications ===")
    
    # Check for ended auctions
    my_auctions = [p for p in products 
                   if p['farmer_username'] == farmer['username'] 
                   and p['is_auction'] 
                   and not p['sold']]
    
    notifications = []
    
    for product in my_auctions:
        end_date = datetime.fromisoformat(product['end_date'])
        if datetime.now() > end_date:
            product_bids = [b for b in bids if b['product_id'] == product['id']]
            if product_bids:
                highest_bid = max(product_bids, key=lambda x: x['amount'])
                notifications.append(f"Auction ended for {product['name']}. Highest bid: {highest_bid['amount']} by {highest_bid['buyer_username']}")
            else:
                notifications.append(f"Auction ended for {product['name']} with no bids.")
    
    if not notifications:
        print("No new notifications.")
    else:
        for note in notifications:
            print(f"- {note}")

# Run the application
if __name__ == "__main__":
    main_menu()