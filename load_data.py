import csv
from datetime import datetime
from app import create_app, db
from app.models.cliente import Cliente
from app.models.proveedor import Proveedor

def load_clientes(csv_path):
    """Carga clientes desde CSV a la BD"""
    print("Cargando clientes...")
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                habeas_data = row['habeas_data'].lower() == 'true'
                fecha_registro = datetime.strptime(row['fecha_registro'], '%Y-%m-%d').date()
                
                cliente = Cliente(
                    id_cliente=row['id_cliente'],
                    tipo_documento=row['tipo_documento'],
                    numero_identificacion=row['numero_identificacion'],
                    nombre_razon_social=row['nombre_razon_social'],
                    email=row['email'],
                    num_contacto=row['num_contacto'],
                    tipo_num_contacto=row['tipo_num_contacto'],
                    ciudad=row['ciudad'],
                    direccion_residencia=row['direccion_residencia'],
                    direccion_operativa=row['direccion_operativa'],
                    representante_legal=row['representante_legal'],
                    habeas_data=habeas_data,
                    tipo_regimen=row['tipo_regimen'],
                    fecha_registro=fecha_registro
                )
                db.session.add(cliente)
                count += 1
                
                if count % 50 == 0:
                    print(f"  {count} clientes procesados...")
            except Exception as e:
                print(f"  Error en fila: {row['id_cliente']} - {str(e)}")
                db.session.rollback()
                continue
        
        db.session.commit()
        print(f"✓ {count} clientes cargados exitosamente")

def load_proveedores(csv_path):
    """Carga proveedores desde CSV a la BD"""
    print("\nCargando proveedores...")
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                habeas_data = row['habeas_data'].lower() == 'true'
                fecha_registro = datetime.strptime(row['fecha_registro'], '%Y-%m-%d').date()
                tiempo_entrega = int(row['tiempo_entrega_promedio'])
                condiciones_pago = int(row['condiciones_pago'])
                calificacion = int(row['calificacion'])
                
                proveedor = Proveedor(
                    id_proveedor=row['id_proveedor'],
                    nombre_razon_social=row['nombre_razon_social'],
                    tipo_documento=row['tipo_documento'],
                    numero_identificacion=row['numero_identificacion'],
                    habeas_data=habeas_data,
                    tipo_regimen=row['tipo_regimen'],
                    rut=row['rut'],
                    ciudad=row['ciudad'],
                    direccion_operativa=row['direccion_operativa'],
                    direccion_residencia=row['direccion_residencia'],
                    email=row['email'],
                    num_contacto=row['num_contacto'],
                    tipo_num_contacto=row['tipo_num_contacto'],
                    representante_legal=row['representante_legal'],
                    banco=row['banco'],
                    tipo_cuenta=row['tipo_cuenta'],
                    numero_cuenta=row['numero_cuenta'],
                    tipo_proveedor=row['tipo_proveedor'],
                    tiempo_entrega_promedio=tiempo_entrega,
                    contacto_comercial=row['contacto_comercial'],
                    contacto_cartera=row['contacto_cartera'],
                    contacto_logistico=row['contacto_logistico'],
                    condiciones_pago=condiciones_pago,
                    calificacion=calificacion,
                    fecha_registro=fecha_registro
                )
                db.session.add(proveedor)
                count += 1
                
                if count % 50 == 0:
                    print(f"  {count} proveedores procesados...")
            except Exception as e:
                print(f"  Error en fila: {row['id_proveedor']} - {str(e)}")
                db.session.rollback()
                continue
        
        db.session.commit()
        print(f"✓ {count} proveedores cargados exitosamente")

if __name__ == '__main__':
    import sys
    
    print("=== Script de Carga de Datos ===\n")
    
    app = create_app()
    with app.app_context():
        # AQUÍ ES LO IMPORTANTE: Crear las tablas primero
        print("Creando tablas...")
        db.create_all()
        print("✓ Tablas creadas\n")
        
        clientes_csv = 'clientes.csv'
        proveedores_csv = 'proveedores.csv'
        
        try:
            load_clientes(clientes_csv)
            load_proveedores(proveedores_csv)
            print("\n✓ ¡Datos cargados exitosamente!")
        except FileNotFoundError as e:
            print(f"Error: No se encontró el archivo - {str(e)}")
            sys.exit(1)
        except Exception as e:
            print(f"Error inesperado: {str(e)}")
            sys.exit(1)