from app import app, db, Log  # Importa app, db y modelo desde tu app principal

with app.app_context():
    numero_prueba = '524611777249'  # Cambia por tu número real
    borrados = Log.query.filter_by(telefono=numero_prueba).delete()
    db.session.commit()
    print(f"Se borraron {borrados} registros para el número {numero_prueba}")
