# 🛒 Vaysed Shop

## 📖 Description
VaysedShop is an e-commerce platform developed with Django, allowing users to browse products, add them to a cart, and place orders with an integrated Monobank payment system. 💳

## ✨ Key Features
* **🖼️ Product Catalog:** View products with detailed descriptions and images.
* **🛒 Shopping Cart:** Add products to the cart, update quantities, and remove items.
* **📝 Checkout Process:** Enter contact information and shipping address.
* **🏦 Monobank Integration:** Secure payment for orders via the Monobank payment gateway.
* **🛠️ Admin Panel:** Manage products, orders, customers, and shipping addresses.
* **📱 Responsive Design:** User-friendly viewing on various devices.
* **👤 Guest Checkout:** Option to place an order without registration.
* **📁 Static and Media File Handling:** Configured serving of static files and product images.

## 💻 Technologies Used
* **Backend:** Python 🐍, Django, Django REST Framework
* **Frontend:** HTML, CSS 🎨, JavaScript 📜
* **Database:** SQLite 🗃️ (default for development)
* **Payment System:** Monobank API 🇺🇦
* **Containerization:** Docker 🐳, Docker Compose
* **Server:** Gunicorn 🦄
* **Static File Handling:** Whitenoise 💨

## 🚀 Setup and Installation
### ✅ Prerequisites
* Python 3.x
* Django
* Other dependencies listed in `requirements.txt`
* Docker and Docker Compose (for running via Docker)

### 🛠️ Local Setup (Windows)
1.  **Cloning the repository:**
    ```bash
    git clone https://github.com/kun3741/vaysedshop/
    cd vaysedshop
    ```
2.  **Creating and activating a virtual environment (recommended):**
    ```bash
    python -m venv env
    .\env\Scripts\activate
    ```
3.  **Installing dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Creating a `.env` file** in the project's root directory (next to `manage.py`) and add the necessary environment variables. Example content for `.env` file:
    ```env
    SECRET_KEY='your_strong_secret_key_here'
    DEBUG=True
    ALLOWED_HOSTS=127.0.0.1,localhost
    MONOBANK_API_TOKEN='your_monobank_api_token_here'
    ```
    * `SECRET_KEY` 🔑: Django secret key. Generate a strong key for production.
    * `DEBUG` 🐛: Set to `False` for production.
    * `ALLOWED_HOSTS` 🌐: List of allowed hosts.
    * `MONOBANK_API_TOKEN` 💳: Your Monobank API token.

5.  **Applying database migrations:**
    ```bash
    python manage.py migrate
    ```
6.  **Creating a superuser (for admin panel access):**
    ```bash
    python manage.py createsuperuser
    ```
7.  **Running the development server:**
    ```bash
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000/`. 🎉

### 🐳 Running with Docker (Windows)
1.  **Ensure Docker and Docker Compose are installed.**
2.  **Create the `.env` file** as described in the previous section. The `docker-compose.yml` file uses this to configure environment variables inside the container.
3.  **Build and run the containers:**
    Open PowerShell or Command Prompt in the project's root directory and run:
    ```bash
    docker-compose up --build
    ```
    The application will be available at `http://localhost:8000/`. 🎊

## 📂 Project Structure (Key Components)
* `vaysedshop/`: Main Django project directory. 🏗️
    * `settings.py`: Project settings. ⚙️
    * `urls.py`: Main project URL routes. 🛣️
    * `wsgi.py` / `asgi.py`: Configuration for WSGI/ASGI servers.
* `shop/`: Django application containing the core shop logic. 🏬
    * `models.py`: Data models (Product, Order, Customer, etc.). 🧱
    * `views.py`: Request handling logic (rendering pages, form processing, API). 🧠
    * `urls.py`: URL routes for the `shop` application.
    * `admin.py`: Configuration for displaying models in the Django admin panel. 👑
    * `utils.py`: Helper functions (e.g., for cart operations). 🛠️
    * `templates/shop/`: HTML templates for pages. 📄
    * `migrations/`: Database migrations. 🔄
* `static/`: Static files (CSS, JavaScript, images). 🖼️
    * `css/main.css`: Main website styles.
    * `js/cart.js`: JavaScript for cart functionality.
    * `js/product_detail.js`: JavaScript for the product detail page.
    * `images/`: Images for design and products.
* `manage.py`: Django command-line utility. ⚙️
* `requirements.txt`: List of Python dependencies. 📋
* `docker-compose.yml`: Configuration for running the project with Docker Compose. 🐳
* `Dockerfile`: Instructions for building the Docker image.
* `BUGREPORT.md`: Report of found and fixed bugs. 🐞
* `CHANGELOG.md`: Project change history. 📜

## 🐞 Bug Reports
* To view a list of identified and fixed bugs, please refer to the `BUGREPORT.md` file. 🧐
