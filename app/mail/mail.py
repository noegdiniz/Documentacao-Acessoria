from flask_mail import Mail

mail = Mail()

def configure(app):
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'workflow@amcel.com.br'
    app.config['MAIL_PASSWORD'] = 'ahxq lnuz kuxf nztg'
    app.config['MAIL_DEFAULT_SENDER'] = 'workflow@amcel.com.br'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    
    mail.init_app(app)
