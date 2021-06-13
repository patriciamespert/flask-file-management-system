from core import create_app 

class Config:
    DEBUG=True

app = create_app(Config)

#app_run
if __name__ == '__main__':
    app.run(debug=True)