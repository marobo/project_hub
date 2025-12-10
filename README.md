# Portfolio Website

A clean, simple personal portfolio website built with Django.

## Features

- 🏠 **Hero Section** - Introduction with call-to-action
- 📁 **Projects Gallery** - Grid display of your work with images and links
- 📬 **Contact Form** - Let visitors reach out to you
- 📱 **Responsive Design** - Works on all devices
- 🎨 **Clean UI** - Modern, minimalist design

## Tech Stack

- **Framework**: Django
- **Database**: SQLite
- **Styling**: Custom CSS

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/project_hub.git
cd project_hub
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Create admin user

```bash
python manage.py createsuperuser
```

### 6. Run the server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to view the site.

## Admin Panel

Access the admin panel at `http://127.0.0.1:8000/admin` to:

- Add/edit projects
- View contact form submissions

## Project Structure

```
project_hub/
├── project_hub/        # Django project settings
├── app_hub/            # Main application
│   ├── models.py       # Project & Contact models
│   ├── views.py        # Views
│   └── admin.py        # Admin configuration
├── templates/          # HTML templates
├── static/css/         # Stylesheets
├── requirements.txt    # Dependencies
└── manage.py
```

## Customization

1. **Update your name**: Edit `templates/home.html` and change "Your Name"
2. **Add social links**: Update links in `templates/base.html` footer
3. **Change colors**: Modify CSS variables in `static/css/style.css`

## License

MIT License

