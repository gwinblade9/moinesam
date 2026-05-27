from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db, User, Request
from functools import wraps
from datetime import datetime

app = Flask(__name__)

# конфигурация
app.secret_key = 'moinesam-premium-cleaning-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cleaning.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# инициализация БД
db.init_app(app)

# создание таблиц и администратора при запуске
with app.app_context():
    db.create_all()
    
    # создание администратора если не существует
    if not User.query.filter_by(login='adminka').first():
        admin = User(
            fullname='Администратор Системы',
            phone='+7 (999) 888-77-66',
            email='admin@moinesam.ru',
            login='adminka',
            password='password',
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Администратор создан: login=adminka, password=password")
    
    print("✅ База данных готова к работе")


def login_required(f):
    """Декоратор: требует авторизации"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('🔐 Пожалуйста, войдите в систему', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Декоратор: требует прав администратора"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('🔐 Пожалуйста, войдите в систему', 'error')
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('⛔ Доступ запрещен. Требуются права администратора.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации"""
    if request.method == 'POST':
        fullname = request.form.get('fullname', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        login = request.form.get('login', '').strip()
        password = request.form.get('password', '').strip()
        
        # валидация
        if not all([fullname, phone, email, login, password]):
            flash('📝 Все поля обязательны для заполнения', 'error')
            return redirect(url_for('register'))
        
        # проверка уникальности логина
        if User.query.filter_by(login=login).first():
            flash('⚠️ Пользователь с таким логином уже существует', 'error')
            return redirect(url_for('register'))
        
        # создание пользователя
        user = User(
            fullname=fullname,
            phone=phone,
            email=email,
            login=login,
            password=password
        )
        db.session.add(user)
        db.session.commit()
        
        flash(f'🎉 Добро пожаловать, {fullname}! Теперь вы можете войти в систему.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Страница авторизации"""
    if request.method == 'POST':
        login = request.form.get('login', '').strip()
        password = request.form.get('password', '').strip()
        
        user = User.query.filter_by(login=login, password=password).first()
        
        if user:
            session['user_id'] = user.id
            session['user_fullname'] = user.fullname
            session['is_admin'] = user.is_admin
            
            flash(f' С возвращением, {user.fullname}! ', 'success')
            
            if user.is_admin:
                return redirect(url_for('admin_panel'))
            return redirect(url_for('dashboard'))
        else:
            flash('❌ Неверный логин или пароль. Попробуйте снова.', 'error')
    
    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    """Личный кабинет пользователя - история заявок"""
    user = User.query.get(session['user_id'])
    user_requests = Request.query.filter_by(user_id=user.id).order_by(Request.created_at.desc()).all()
    
    return render_template('dashboard.html', user=user, requests=user_requests)


@app.route('/create_request', methods=['GET', 'POST'])
@login_required
def create_request():
    """Страница создания новой заявки"""
    if request.method == 'POST':
        address = request.form.get('address', '').strip()
        contact_phone = request.form.get('contact_phone', '').strip()
        service_type = request.form.get('service_type')
        preferred_date = request.form.get('preferred_date')
        preferred_time = request.form.get('preferred_time')
        payment_type = request.form.get('payment_type')
        
        # валидация
        if not all([address, contact_phone, service_type, preferred_date, preferred_time, payment_type]):
            flash('📝 Все поля обязательны для заполнения', 'error')
            return redirect(url_for('create_request'))
        
        # создание заявки
        new_request = Request(
            user_id=session['user_id'],
            address=address,
            contact_phone=contact_phone,
            service_type=service_type,
            preferred_date=preferred_date,
            preferred_time=preferred_time,
            payment_type=payment_type,
            status='новая заявка'
        )
        db.session.add(new_request)
        db.session.commit()
        
        flash('✅ Заявка успешно создана! Мы свяжемся с вами в ближайшее время.', 'success')
        return redirect(url_for('dashboard'))
    
    service_types = [
        '🧹 Общий клининг',
        '🏠 Генеральная уборка',
        '🔨 Послестроительная уборка',
        '🛋️ Химчистка ковров и мебели'
    ]
    payment_types = ['💵 Наличные', '💳 Банковская карта']
    
    return render_template('create_request.html', service_types=service_types, payment_types=payment_types)


@app.route('/admin')
@admin_required
def admin_panel():
    """Панель администратора"""
    all_requests = Request.query.order_by(Request.created_at.desc()).all()
    
    # данные заявок с информацией о пользователях
    requests_data = []
    for req in all_requests:
        user = User.query.get(req.user_id)
        requests_data.append({
            'request': req,
            'user': user
        })
    
    # Статистика
    stats = {
        'total': len(all_requests),
        'new': len([r for r in all_requests if r.status == 'новая заявка']),
        'in_progress': len([r for r in all_requests if r.status == 'в работе']),
        'completed': len([r for r in all_requests if r.status == 'выполнено']),
        'cancelled': len([r for r in all_requests if r.status == 'отменено'])
    }
    
    return render_template('admin.html', requests_data=requests_data, stats=stats)



@app.route('/admin/update_status/<int:request_id>', methods=['POST'])
@admin_required
def update_status(request_id):
    req = Request.query.get_or_404(request_id)
    new_status = request.form.get('status')
    
    if new_status == 'отменено':
        cancel_reason = request.form.get('cancel_reason', '').strip()
        if not cancel_reason:
            flash('⚠️ При отмене заявки необходимо указать причину!', 'error')
            return redirect(url_for('admin_panel'))
        req.cancel_reason = cancel_reason
        req.status = 'отменено'
        flash(f'❌ Заявка #{request_id} отменена. Причина: {cancel_reason}', 'success')
    else:
        req.status = new_status
        req.cancel_reason = ''
        if new_status == 'в работе':
            flash(f'🔧 Заявка #{request_id} взята в работу', 'success')
        elif new_status == 'выполнено':
            flash(f'✅ Заявка #{request_id} отмечена как выполненная', 'success')
        elif new_status == 'новая заявка':
            flash(f'📝 Статус заявки #{request_id} изменен на "Новая"', 'success')
    
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/logout')
def logout():
    """Выход из системы"""
    session.clear()
    flash('👋 Вы вышли из системы. Ждем вас снова!', 'info')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
