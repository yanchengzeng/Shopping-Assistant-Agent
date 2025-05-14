import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from storage.db_model import Base, Product

# Sample data
SAMPLE_DATA = {
    'white_sofa.jpg': {
        'name': 'Nouvelle Revolution White Sofa',
        'desc': "Experience ultimate comfort and modern style with this plush, cream-colored sofa. Featuring smooth, rounded edges and a minimalist design, it adds a touch of elegance to any living space. Upholstered in soft, durable fabric, this sofa is perfect for relaxing, entertaining, or simply elevating your home's contemporary décor.",
        'category': 'furniture',
        'brand': 'Lewis',
        'price': 500,
        'image_url': 'data/images/white_sofa.jpg'
    },
    'black_sofa.jpg': {
        'name': 'Navy Blue Velvet Sofa with Turned Wooden Legs',
        'desc': "Elevate your living space with this stylish navy blue velvet sofa, designed for both elegance and comfort. With its plush cushioning, supportive back pillows, and classic turned wooden legs, this sofa offers a cozy spot for relaxation while adding a touch of sophistication to any modern or traditional home décor.",
        'category': 'furniture',
        'brand': 'Johnson',
        'price': 1500,
        'image_url': 'data/images/black_sofa.jpg'
    },
    'colorful_jeans.jpg': {
        'name': 'Vibrant Multicolor High-Waisted Statement Pants',
        'desc': "Stand out in style with these eye-catching, high-waisted pants featuring a vibrant, multicolored print of whimsical characters and geometric patterns. Crafted from comfortable fabric, these trousers are perfect for making a bold fashion statement at any event or party. Add a pop of color and creativity to your wardrobe today!",
        'category': 'clothing',
        'brand': 'Lewis',
        'price': 20,
        'image_url': 'data/images/colorful_jeans.jpg'
    },
    'black_jeans.jpg': {
        'name': 'Classic Black Skinny Jeans',
        'desc': "Enhance your wardrobe with these classic black skinny jeans, designed for a sleek and modern fit. Crafted from comfortable stretch denim, they offer effortless style and flexibility for everyday wear. Perfect for pairing with any top, these versatile jeans are a must-have staple for any fashion-forward collection.",
        'category': 'clothing',
        'brand': 'Johnson',
        'price': 150,
        'image_url': 'data/images/black_jeans.jpg'
    },
    'white_tshirt.jpg': {
        'name': 'Nouvelle Revolution White Graphic Tee',
        'desc':"Highlight your casual style with this chic white graphic tee, featuring a bold 'Nouvelle Revolution' print for a trendy, effortless look. Designed for a petite fit, this soft cotton shirt pairs perfectly with jeans or skirts for versatile everyday wear. Make a statement in comfort and style!",
        'category': 'clothing',
        'brand': 'Lewis',
        'price': 20,
        'image_url': 'data/images/white_tshirt.jpg'
    },
    'black_tshirt.jpg': {
        'name': 'Classic Navy Blue T-Shirt',
        'desc': "Light up your day with this classic navy blue t-shirt, featuring a subtle chest print for a modern edge. Made from soft, breathable fabric, it's perfect for everyday wear. Pair effortlessly with jeans or joggers for a clean, versatile look that never goes out of fashion.",
        'category': 'clothing',
        'brand': 'Johnson',
        'price': 150,
        'image_url': 'data/images/black_tshirt.jpg'
    },
    'night_tv.jpg': {
        'name': 'Ultra-Slim 4K Smart LED TV',
        'desc':"With its breathtaking clarity and vibrant colors, our ultra-slim 4K Smart LED TV will provide you with your favorite movies, shows, and games on a stunning widescreen display that brings every detail to life. With sleek modern design and easy connectivity, this television is perfect for any modern home entertainment setup.",
        'category': 'electronics',
        'brand': 'Lewis',
        'price': 500,
        'image_url': 'data/images/night_tv.jpg'
    },
    'ocean_tv.jpg': {
        'name': 'Sleek Flat-Screen LED TV with Slim Bezels',
        'desc': "Enjoy stunning visuals with this sleek flat-screen LED TV, designed to deliver vibrant colors and sharp details for all your favorite movies, shows, and games. Its slim bezels and modern stand make it a perfect fit for any room, blending seamlessly with your home décor while providing immersive entertainment.",
        'category': 'electronics',
        'brand': 'Johnson',
        'price': 1500,
        'image_url': 'data/images/ocean_tv.jpg'
    }
}

def init_db():
    # Get the project root directory (two levels up from this script)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Create data directory in project root if it doesn't exist
    data_dir = os.path.join(project_root, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Create SQLite database in the data directory
    db_path = os.path.join(data_dir, 'products.db')
    engine = create_engine(f'sqlite:///{db_path}')
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Add all products to the database
        for image_name, product_data in SAMPLE_DATA.items():
            product = Product(
                name=product_data['name'],
                desc=product_data['desc'],
                category=product_data['category'],
                brand=product_data['brand'],
                price=product_data['price'],
                image_url=product_data['image_url']
            )
            session.add(product)
        
        # Commit the changes
        session.commit()
        print(f"Database initialized successfully at {db_path}!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    init_db() 