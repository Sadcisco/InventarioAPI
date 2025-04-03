from app import create_app
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = create_app()

@app.route('/')
def home():
    return {'message': 'API funcionando'}

@app.errorhandler(500)
def handle_500_error(error):
    logger.error(f"Error interno del servidor: {error}")
    return {'error': str(error), 'tipo': type(error).__name__}, 500

if __name__ == "__main__":
    logger.info("Iniciando servidor API...")
    app.run(debug=True, host='0.0.0.0', port=5000)
