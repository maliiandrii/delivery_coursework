#  Delivery Service Web Application

---

##  Overview

Delivery Service is a course work project that supports the delivery process by connecting customers with couriers. The platform provides an intuitive interface for browsing products, placing orders, and tracking deliveries in real-time.

---

##  Features

###  For Customers

  - Search products and filter them
  - Add products to cart
  - Create orders with delivery details
  - Track order status in real-time
  - Order history with full details
  - Leave reviews for completed deliveries

### For Couriers

  - View available orders waiting for acceptance
  - See assigned active deliveries
  - Accept orders with one click

###  For Administrators

  - Manage users (customers and couriers)
  - CRUD operations for products and categories
  - Monitor all orders in the system
  - Moderate reviews

---

##  Tech Stack

### Backend
- **Framework**: Django 4.2
- **Language**: Python 3.10+
- **Database**: PostgreSQL 15
- **ORM**: Django ORM
- **Testing**: Django TestCase

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with custom properties
- **JavaScript** - Vanilla JS for interactions

### Development Tools
- **PyCharm** - Python IDE
- **WebStorm** - Frontend development
- **Docker** - Containerization
- **Git** - Version control

---

##  Installation

**Clone the repository**
```bash
git clone https://github.com/maliiandrii/delivery-service.git
cd delivery-service
```

### Docker Installation

```bash
# Build and start containers
docker-compose up --build

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Load sample data
docker-compose exec web python manage.py populate_data
```

---


## Author

**Andrii Malii IP-32**
- Course work for a web application for delivery service support
- University: National Technical University of Ukraine "Igor Sikorsky Kyiv Polytechnic Institute"
