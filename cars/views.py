from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Car, Reservation
from django.core.paginator import Paginator
from contacts.models import Contact
from django.core.files.storage import FileSystemStorage
from torchvision import models, transforms
from PIL import Image
import torch
import torch.nn.functional as F
import cv2
import numpy as np

# 🎨 Enhanced color name detection

def closest_color_name(rgb):
    r, g, b = rgb
    brightness = (r + g + b) / 3

    if brightness < 50:
        return 'black'
    elif brightness > 240:
        return 'white'

    known_colors = {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'gray': (128, 128, 128),
        'silver': (192, 192, 192),
        'red': (255, 0, 0),
        'blue': (0, 0, 255),
        'green': (0, 128, 0),
        'yellow': (255, 255, 0),
        'orange': (255, 165, 0),
        'brown': (139, 69, 19),
        'purple': (128, 0, 128),
        'pink': (255, 192, 203)
    }

    def distance(c1, c2):
        return sum((a - b) ** 2 for a, b in zip(c1, c2))

    return min(known_colors, key=lambda name: distance(rgb, known_colors[name]))


def get_dominant_color(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, (100, 100))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    pixels = img.reshape((-1, 3))
    mask = np.all(pixels < [240, 240, 240], axis=1)  # Remove near-white
    filtered = pixels[mask] if np.any(mask) else pixels

    Z = np.float32(filtered)
    K = 3
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(Z, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    counts = np.bincount(labels.flatten())
    dominant_rgb = centers[np.argmax(counts)].astype(int)
    return closest_color_name(tuple(dominant_rgb))


@login_required
def image_search(request):
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            img_file = request.FILES['image']
            fs = FileSystemStorage()
            filename = fs.save(img_file.name, img_file)
            path = fs.path(filename)

            model = models.mobilenet_v2(pretrained=True)
            model.classifier = torch.nn.Identity()
            model.eval()

            preprocess = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])

            def get_embedding(image_path):
                try:
                    img = Image.open(image_path).convert('RGB')
                    tensor = preprocess(img).unsqueeze(0)
                    with torch.no_grad():
                        return model(tensor).squeeze()
                except:
                    return None

            uploaded_vec = get_embedding(path)
            color_guess = get_dominant_color(path)
            print("🎨 Color detected:", color_guess)

            matches = []
            for car in Car.objects.filter(stock__gt=0):
                car_vec = get_embedding(car.car_photo.path)
                if car_vec is None:
                    continue
                sim = F.cosine_similarity(uploaded_vec, car_vec, dim=0).item()
                matches.append((sim, car))

            matches.sort(key=lambda x: -x[0])
            threshold = 0.8
            similar = [c for s, c in matches if s >= threshold]

            if not similar:
                similar = Car.objects.filter(color__icontains=color_guess, stock__gt=0)
                message = f"❌ No match. Showing cars by color: '{color_guess}'"
            else:
                message = f"✅ Found {len(similar)} similar car(s) by image match."

            return render(request, 'cars/search.html', {'cars': similar, 'message': message})

        except Exception as e:
            print("❌ Search error:", e)
            return render(request, 'cars/search.html', {'cars': [], 'message': 'Image search failed.'})

    return redirect('cars')


# 🛍️ Reserve a car
@login_required
def buy_car(request, id):
    car = get_object_or_404(Car, pk=id)
    if request.method == 'POST':
        Reservation.objects.create(
            user=request.user,
            car=car,
            booking_method=request.POST.get('booking_method'),
            visit_date=request.POST.get('visit_date'),
            delivery_address=request.POST.get('delivery_address')
        )
        return redirect('dashboard')
    return render(request, 'cars/buy_car.html', {'car': car})

# ❌ Cancel a reservation
@login_required
def cancel_reservation(request, id):
    reservation = get_object_or_404(Reservation, pk=id, user=request.user)
    reservation.delete()
    return redirect('dashboard')

# 🛍️ Show available cars
def cars(request):
    cars = Car.objects.filter(stock__gt=0).order_by('-created_date')
    paginator = Paginator(cars, 4)
    page = request.GET.get('page')
    paged_cars = paginator.get_page(page)

    model_search = Car.objects.values_list('model', flat=True).distinct()
    city_search = Car.objects.values_list('city', flat=True).distinct()
    year_search = Car.objects.values_list('year', flat=True).distinct()
    body_style_search = Car.objects.values_list('body_style', flat=True).distinct()

    data = {
        'cars': paged_cars,
        'model_search': model_search,
        'city_search': city_search,
        'year_search': year_search,
        'body_style_search': body_style_search,
    }
    return render(request, 'cars/cars.html', data)

# 📄 Car detail
def car_detail(request, id):
    single_car = get_object_or_404(Car, pk=id)
    if single_car.stock <= 0:
        return redirect('cars')
    return render(request, 'cars/car_detail.html', {'single_car': single_car})

# 🔎 Search with filters
def search(request):
    cars = Car.objects.filter(stock__gt=0).order_by('-created_date')

    model_search = Car.objects.values_list('model', flat=True).distinct()
    city_search = Car.objects.values_list('city', flat=True).distinct()
    year_search = Car.objects.values_list('year', flat=True).distinct()
    body_style_search = Car.objects.values_list('body_style', flat=True).distinct()
    transmission_search = Car.objects.values_list('transmission', flat=True).distinct()

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            cars = cars.filter(description__icontains=keyword)

    if 'model' in request.GET:
        model = request.GET['model']
        if model:
            cars = cars.filter(model__iexact=model)

    if 'city' in request.GET:
        city = request.GET['city']
        if city:
            cars = cars.filter(city__iexact=city)

    if 'year' in request.GET:
        year = request.GET['year']
        if year:
            cars = cars.filter(year__iexact=year)

    if 'body_style' in request.GET:
        body_style = request.GET['body_style']
        if body_style:
            cars = cars.filter(body_style__iexact=body_style)

    if 'min_price' in request.GET:
        min_price = request.GET['min_price']
        max_price = request.GET['max_price']
        if max_price:
            cars = cars.filter(price__gte=min_price, price__lte=max_price)

    data = {
        'cars': cars,
        'model_search': model_search,
        'city_search': city_search,
        'year_search': year_search,
        'body_style_search': body_style_search,
        'transmission_search': transmission_search,
    }
    return render(request, 'cars/search.html', data)



